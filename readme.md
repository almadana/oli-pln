# NLP for ECOSud Project, "Oli" and "Vaca"

Self explanatory 'data' and 'scripts' folders.


## Library requirements

To review and edit the alignments, and to extract pitch and formant data we used Praat (6.1.38)

Here's an incomplete list of all the python libraries:

- MFA - Montreal Force Alignment (2.0). (Separate python environment encouraged). 

conda config --add channels conda-forge
conda install montreal-forced-aligner

After installation, download the french model and dictionary: 

mfa models download acoustic french_mfa
mfa models download dictionary french_mfa

- Torch (1.11.0) - pip install torch

- Transformers (4.20.0) - from HuggingFace. pip install tpipransformers


## Analysis pipeline

- Transcribe audio .wav files with Google Cloud (or other speech2Text service or software)

- Run process_json.py to extract json files to plain text

- Manually inspect and modify transcription plain text files if necessary (it probably is). Make sure these files have ONLY ONE LINE of text!!

- Move revised plain text files to the "wavfiles" folder in 'data'. Rename them to match the name of each wavefile (keep the .txt extension). Put each pair of txt and wav files (e.g. renard1 and renard2) on a new subfolder. The structure should be something like ./data/wavfiles/{renard,nadine,etc}/{renard,nadine,etc}{1,2}.{txt,wav}

- (Separate python environment encouraged) Run maf to validate and align transcriptions to wav files. 

Example: 
mfa validate ./wavfiles french_mfa french_mfa
mfa align --clean ./wavfiles french_mfa french_mfa ./wavfiles/aligned

- Open each wav and textGrid file with Praat and revise for inconsistencies and misalignments (if you want a complete annotation of all the phonemes, that's going to take some work...)

- Save the revised textGrid files to the ./revised subfolder

- Run embed_main.py

- There should be now a file named embed.mat in the data folder

    The structure is as follows:
        - A n-by-1 cell array with each filename
        - A n-by-1 cell array with morphoeme markings. Each cell contains a timepoints-by-2 matrix. onset and offset are the columns
        - A cell array with morphemes. Each cell contains a char-array of timepoints-by-width, where width is the max number of characters (uses right-padding). Ideally should be one... but maybe not
        - A cell array with prediction "probabilities". Each cell contains a timepoints-by-3 matrix: onset, offset and "prob" and the columns.
        - A n-by-1 cell array with the text markings. Each cell contains a char-array of timepoints-by-width, where width is the max number of characters (uses right-padding).
        
To obtain pitch and forman data from the audio files:

- Open all audio files in Praat (all at once if you're feeling lucky)

- Open the pitch_extractor.praat script

- Run the script once for each audio file (you should write the name of the corresponding Sound object as it appears on the list, but without the number. For instance: Sound renard1)

- You can provide a corresponding output filename (renard_pitch.csv)

- I'm not sure where Praat is going to create each output file. Probably in either a) the Home folder, or b) the last folder in which you saved a file during this session. You can save a bogus file at the corresponding folder just to make things easy when you export the csv files.

- After processig each Sound object, remove it, as well as its newly created Formant and Pitch objects (may not be necessary but it's cleaner, right?)

- Have fun!
