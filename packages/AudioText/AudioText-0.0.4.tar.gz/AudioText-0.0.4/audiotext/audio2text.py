def translator(path):
    import speech_recognition as sr 
    import os 
    from pydub import AudioSegment
    from pydub.silence import split_on_silence
    r = sr.Recognizer()
    def get_large_audio_transcription(path):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)  
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
            # experiment with this value for your target audio file
            min_silence_len = 500,
            # adjust this per requirement
            silence_thresh = sound.dBFS-14,
            # keep the silence for 1 second, adjustable as well
            keep_silence=500,
        )
        folder_name = "audio-chunks"
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk 
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_google(audio_listened,language='ar-AR')
                   # print(text)
                    f=open('text.txt','w',encoding='utf-8')
                    f.writelines(text+'\n')
                    f.close()
                except sr.UnknownValueError as e:
                    print("", str(e))
                else:
                    text = f"{text.capitalize()}. "
                   # print(chunk_filename, ":", text)
                    whole_text += text
        # return the text for all chunks detected
        return text#whole_text
    #path = "falahgs.wav"
    #path="out.wav"
   # print("\nFull text:", get_large_audio_transcription(path))
    text=get_large_audio_transcription(path)
   # text
    #get_large_audio_transcription(path)
    #read text file in text variable
   # with open('text.txt','r') as file:
       # countriesStr = file.read()
   # print(countriesStr)
    from googletrans import Translator
    translator = Translator()
    translated_text = translator.translate(text)
    print(translated_text.text)
    def Replace(str1):
        maketrans = str1.maketrans
        final = str1.translate(maketrans(',.', '.,'))
        return final.replace(',', ", ")
    # Driving Code
    prompts = translated_text.text
   # print(Replace(prompts))
    prompts = prompts
    prompts = prompts[:77]
   # print(prompts)
