from google.cloud import translate_v2 as translate
import six
import subprocess
import xml.etree.ElementTree as ET
import subprocess
import os
import math
import shutil
import sys
import time
from convert import *

class Translation_pipeline():
    
    def __init__(self, file_path = None, save_path = None, target_language = None):
        """
        Args:
            file_path: transformed odt file path which will be translated
            save_path: path to store the translated files
            target_language: english text will be translated to the target language
                            languages can be:- Hindi, Chinese, Arabic, Polish, Spanish, Tagalog
        """
        self.file_path = file_path
        self.save_path = save_path
        self.target = target_language
    
    @staticmethod
    def convert2odt(file_path, save_path):
        """Convert any input file to odt format
        Args:
            path_to_file: file path where input file is stored
            save_path: file path where the converted odt file will be stored

        Returns:
            None
        """
        command = ['unoconv', '-o', save_path , '-f', 'odt', file_path] 
        # for the command to run: sudo apt install libreoffice
        code = subprocess.run(command)
        
    @staticmethod
    def convert2docx(file_path, save_path):
        """Convert any input file to docx format
        Args:
            path_to_file: file path where input file is stored
            save_path: file path where the converted docx file will be stored

        Returns:
            None
        """
        command = ['unoconv', '-o', save_path , '-f', 'docx', file_path] 
        # for the command to run: sudo apt install libreoffice
        code = subprocess.run(command)
    
    @staticmethod
    def convert2pdf(file_path, save_path):
        """Convert any input file to pdf format
        Args:
            path_to_file: file path where input file is stored
            save_path: file path where the converted pdf file will be stored

        Returns:
            None
        """
        command = ['unoconv', '-o', save_path , '-f', 'pdf', file_path] 
        # for the command to run: sudo apt install libreoffice
        code = subprocess.run(command)
    
    
    def translate_text(self, text):
        """Translates text into the target language.
        Target must be an ISO 639-1 language code.
        See https://g.co/cloud/translate/v2/translate-reference#supported_languages
        Args:
            target_language: can be any of the six language given- Hindi, Chinese, Arabic, Polish, Spanish, Tagalog
            text: input text which needs to be translated of type string

        Returns:
            translated_text: translated text in target language of type string 
        """
        Target = {'Hindi': 'hi','Chinese':'zh-TW', 'Arabic':'ar','Polish':'pl', 'Spanish':'es', 'Tagalog':'tl'}
        target = Target[self.target]
        translate_client = translate.Client()

        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        # Text can also be a sequence of strings, in which cas"e this method
        # will return a sequence of results for each text.
        result = translate_client.translate(text, target_language=target)

        translated_text = result["translatedText"]
        return translated_text

    def get_weight_list(self, distribution_list):
        """This function is similar to argmax probability distribution function. 
        Devides every number in the list with the sum of list such that the new sum of list should be 1.
        Args:
            distribution_list: (list of numbers of type integer) No of text words in sub-element text or 
            tail feild appended sequentially in a list
            
        Returns:
            wt_list (list of numbers of type float): Argmax probability distribution of wt_list
            
        example:
            [1, 2, 3] ==> [0.166, 0.333, 0.5]
        """
        total_sum = sum(distribution_list)
        wt_list = []
        for i in distribution_list:
            wt_list.append(i/total_sum)
        return wt_list

    def split_on_weights(self, my_list, weight_list):
        """Splits the translated text words list in accordance with the weight list received from get_weight_list func.
        Args:
            my_list (list of string words): List of translated words. After a sentence is translated... it is split 
                                            using translated_text.split(' ').
            weight_list (list of numbers of type float): probability distribution list on no of words present in the 
                                            children tag in parent p tag
        Returns:
            sublists (list of lists -> inside list is list of string (english words)): Splitted list into multiple sub-lists 
            
        example:
            [1,2,3,4,5,6,7,8,9,10], [0.5, 0.5] ==> [[1,2,3,4,5], [6,7,8,9,10]] 
        """
        sublists = []
        prev_index = 0
        for weight in weight_list:
            next_index = prev_index + math.ceil( (len(my_list) * weight) )

            sublists.append( my_list[prev_index : next_index] )
            prev_index = next_index

        return sublists

    def make_sublist_string(self, split_list):
        """Make a string sentence of words from individual string words in a list. Hence, every sublist in the 
        main list will be converted to a sentence from list of words.
        Args:
            split_list(list of lists -> inside list is list of strings (english words))
        
        Returns:
            string_list: list of string sentences
            
        example:
            [['hello', 'world'],['hi','there']] ==> ['hello world', 'hi there']
        
        """
        string_list = []
        for sub_list in split_list:
            temp = ' '.join(sub_list[:])
            string_list.append(temp)
        return string_list

    def translate_odt_document(self):
        """Extracts english text and replaces it with translated text in odt file. Odt file internally
        is a zip of multiple files and folders. In odt, the text is stored in content.xml.... Use 7zip
        to extract the content.xml -> extract the english text using xml parser ->
        translate and replace the english text in the xml file -> save the odt file -> convert it to pdf
        Args:
            self: will use class initiated params

        Returns:
            None
        """
        
        # extracts content.xml from odt
        subprocess.run(['7z','e',self.file_path,'content.xml',f'-o{self.save_path}'])

        # parse the xml file
        content_path = os.path.join(self.save_path, 'content.xml')
        tree = ET.parse(content_path)
        print(tree, content_path)

        # iterate through every tag in xml dom
        for elem in tree.iter():
            tag_end = elem.tag.split('}')[-1]
            org_text = None # ALL TEXT INCUDING FLOATING TEXT (tail text)
            if(tag_end == 'p' or tag_end == 'h'):
                org_text = ''.join(elem.itertext())
            
            # Not every tag will have a text and every text will be in p tag. Hence, we will find
            # if we have any text inside the p tag or any of its child tag
            if(org_text != None and len(org_text) >= 1):
                sub_text = '' # TEXT INSIDE ALL CHILD 
                text_distribution = [] # no of words in every child tag
                cnt = 0

                for sub_elem in elem.iter():
                    if(sub_elem.text != None):
                        sub_text += '' + str(sub_elem.text)
                        text_distribution.append(len((sub_elem.text).split(' ')))
                        cnt += 1

                    if(sub_elem.tail != None):
                        sub_text += '' + str(sub_elem.tail)
                        text_distribution.append(len((sub_elem.tail).split(' ')))
                        cnt += 1

                # parent p tag getting translated
                translated_text = self.translate_text(org_text)
#                 print(org_text,'\n',translated_text,'\n\n')
                translated_text = translated_text.split(' ')

                wt_list = self.get_weight_list(text_distribution)
                translated_text = self.split_on_weights(translated_text, wt_list)
                translated_text = self.make_sublist_string(translated_text)

                text_counter = 0
                # replacing every existing english text with the translated text.
                for sub_elem in elem.iter():

                    if(sub_elem.text != None):
                        sub_elem.text = translated_text[text_counter] + ' '
                        text_counter += 1

                    if(sub_elem.tail != None):
                        sub_elem.tail = translated_text[text_counter] + ' '
                        text_counter += 1
        
        # write back the tree back to xml. The new xml contains the translated text
        tree.write(content_path)
        
        # Remove the original content.xml from the english odt. Then add the new xml inside 
        # the odt and delete the new xml from the current file directory
        subprocess.run(['7z','d',self.file_path,'content.xml'])
        subprocess.run(['7z','a',self.file_path,content_path])
        subprocess.run(['rm','-f',content_path])
        print("File successfully translated...")
        
def wait_sometime(file_path):
    """
    Returns:
        file_path: success
        'Operation Failed': Failure
    """
    cnt = 0
    while(True):
        if(os.path.isfile(file_path)):
            return file_path
        elif(cnt <= 7):
            time.sleep(1)
            cnt += 1
        else:
            return "Operation Failed"
    
def translate_pipeline(file_path, save_path, target):
    """ Incorporates translation pipeline class.
    Args:
        file_path: Input file path (can be docx, doc, txt, rtf, odt, pdf)
        save_path: Path where the translated document will be saved
        target_language: english text will be translated to the target language
                        languages can be:- Hindi, Chinese, Arabic, Polish, Spanish, Tagalog
                        
    Returns:
        odt_file_path: path where translated odt document is stored
        pdf_file_path: path where translated pdf document is stored
    """
    try:
        if(os.path.isfile(file_path)):
            print("File identified")
            file_path = run_conversion(file_path, save_path)
        else:
            print("File is not present at source")
            sys.exit(1)
        
        name = file_path.split('/')[-1]
        true_name = name.rsplit('.', 1)[0]  # file_name without file_path 
        print(name, true_name)
        output_type = name.split('.')[-1] # output type (pdf,docx,odt,etc) of the input file

        odt_name = true_name+'_'+target+'_translated.odt'
        odt_file_path = os.path.join(save_path, odt_name)

        pdf_name = true_name+'_'+target+'_translated.pdf'
        docx_name = true_name+'_'+target+'_translated.docx'

        if(output_type != 'odt'): # convert to odt if the file is already not in odt file format
            Translation_pipeline.convert2odt(file_path, odt_file_path)
            saved_file_path = os.path.join(save_path, true_name+'.odt')
            operation = wait_sometime(odt_file_path)

            if(os.path.isfile(odt_file_path)):
                print("converted to odt and renamed: ",operation)
            else:
                print("File was not able to convert to odt")
                sys.exit(1)
        else:
            shutil.move(file_path, odt_file_path)
            operation = wait_sometime(odt_file_path)
            print("Renamed odt: ",operation)
            
            if(os.path.isfile(odt_file_path)):
                print("File type already in type: odt and successfully moved and renamed")
            else:
                print("Odt file did not get moved or renamed")
                sys.exit(1)

        # translate to target language
        pipeline_obj = Translation_pipeline(odt_file_path, save_path, target)
        pipeline_obj.translate_odt_document()
        
        #check if odt is present or not
        if(odt_file_path):
            print("Translated File saved")
        else:
            odt_file_path = None
        
        # convert to pdf
        pdf_file_path = os.path.join(save_path, pdf_name)
        Translation_pipeline.convert2pdf(odt_file_path, pdf_file_path) 
        
        operation = wait_sometime(pdf_file_path)
        print("odt to pdf: ",operation)
        if(os.path.isfile(pdf_file_path)):
            print("Translated file successfully converted to pdf file format")
        else:
            pdf_file_path = None
            
        # convert to docx
        docx_file_path = os.path.join(save_path, docx_name)
        Translation_pipeline.convert2docx(odt_file_path, docx_file_path) 
        
        operation = wait_sometime(docx_file_path)
        print("odt to docx: ",operation)
        if(os.path.isfile(docx_file_path)):
            print("Translated file successfully converted to docx file format")
        else:
            docx_file_path = None
            
        # return the file path of translated odt and translated pdf file
        return odt_file_path, pdf_file_path, docx_file_path
    
    except Exception as e:
        print("Translation Pipeline Failed")
        print(e)