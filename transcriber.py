import math
from transformers import pipeline
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from os import path
from pydub import AudioSegment


class Transcription():

    def convert_mp3_to_wav(self, src, dst):
        print('Converting started')
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        print('Converting ended')

    # a function that splits the audio file into chunks
    # and applies speech recognition

    def get_large_audio_transcription(self, path):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        print('Transcription started')
        # create a speech recognition object
        r = sr.Recognizer()

        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
                                  # experiment with this value for your target audio file
                                  min_silence_len=700,
                                  # adjust this per requirement
                                  silence_thresh=sound.dBFS-14,
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
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(f'sentence {i}', ":", text)
                    whole_text += text
        # return the text for all chunks detected
        print('Transcription end')
        return whole_text

    def make_summarization(self, whole_text: str) -> str:
        print('Summarization started')
        print('Length whole text: ', len(whole_text))
        summarizer = pipeline("summarization")

        pic = len(whole_text) / 4000
        pic = int(math.ceil(pic))

        summary = ""

        for i in range(0, int(pic)):
            border = len(whole_text) / int(pic)
            increment_i = i+1
            print(border*i, border*increment_i)

            curr_article = whole_text[int(border*i): int(border*increment_i)]
            curr_summary = summarizer(curr_article, max_length=130, min_length=30,
                                      do_sample=False)
            summary = summary + list(curr_summary[0].values())[0]

        print('Summarization ended')
        return summary

    def save_all(self, summary, whole_text):
        print('Saving started')
        with open("Output.txt", "w") as text_file:
            text_file.write("Summary:\n")
            text_file.write(summary)
            text_file.write("\n\n")
            text_file.write("Text:\n")
            text_file.write(whole_text)
        print('Saving ended')


def main():
    src = "sample.mp3"
    path = "sample.wav"

    trans = Transcription()

    trans.convert_mp3_to_wav(src, path)
    whole_text = trans.get_large_audio_transcription(path)
    summary = trans.make_summarization(whole_text)

    trans.save_all(summary, whole_text)


if __name__ == "__main__":
    main()
