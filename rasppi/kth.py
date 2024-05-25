from gtts import gTTS
import easyocr

def is_kannada_word(word):
    # Unicode range for Kannada characters is 0x0C80 to 0x0CFF
    return any('\u0C80' <= char <= '\u0CFF' for char in word)

def extract_kannada_words(result):
    kannada_words = ""
    for item in result:
        word = item[1]  # Extract the text part from the detection result
        if is_kannada_word(word):
            kannada_words += word + " "
    return kannada_words.strip()

def main():

    reader = easyocr.Reader(['kn']) 
    image_path = 'kann.jpg'
    result = reader.readtext(image_path) 
    kannada_words = extract_kannada_words(result)
    tts = gTTS(kannada_words, lang='kn')
    tts.save('hello.mp3')
    print(kannada_words)

if __name__ == "__main__":
    main()
