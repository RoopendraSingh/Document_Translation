from google.cloud import translate
import argparse

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

#     print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
#     print(u"Detected source language: {}\n".format(result["detectedSourceLanguage"]))

# def get_translated_text():
#     Target = {'Hindi': 'hi','Chinese':'zh', 'German':'de','French':'pt'}
#     Text = "hello Deependra how are you?  Who are you? How is your preparation for MPPSC going on?"

#     language = ['French', 'Hindi', 'Chinese']

#     for i in language:
#         translate_text(Target[i], Text)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--language_1', dest='translate_into_language_1', type=str, help='translate into', required=True)
    parser.add_argument('--language_2', dest='translate_into_language_2', type=str, help='translate into', required=True)
    parser.add_argument('--language_3', dest='translate_into_language_3', type=str, help='translate into', required=True)
    parser.add_argument('--language_4', dest='translate_into_language_4', type=str, help='translate into', required=True)

    print(parser.parse_args())
    args = parser.parse_args()

    language_1=args.translate_into_language_1
    language_2=args.translate_into_language_2
    language_3=args.translate_into_language_3
    language_4=args.translate_into_language_4
    
    
    Lang = [language_1, language_2, language_3, language_4]
    print(Lang)
    
    Target = {'Hindi': 'hi','Chinese':'zh', 'German':'de','French':'pt', 'Urdu':'ur'}
    Text = "hello Deependra how are you?  Who are you? How is your preparation for MPPSC going on?"
    print(u"Text: {}".format(Text))
    
# #     language = ['French', 'Hindi', 'Chinese']
    for language in Lang:
        if (language == ''):
            continue
        translate_text(Target[language], Text)
#         translate_text(Target[language_2], Text)
#         translate_text(Target[language_3], Text)
#         translate_text(Target[language_4], Text)
