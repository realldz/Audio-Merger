import logging
import math
from PyQt5.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

logger = logging.getLogger(__name__)

def remove_silence(audio_segment, silence_thresh=-60.0, chunk_size=10):
    logger.debug(f"Removing silence with threshold={silence_thresh}dBFS and chunk_size={chunk_size}ms")
    logger.debug(f"Original duration: {len(audio_segment)}ms")
    logger.debug(f"Original dBFS: {audio_segment.dBFS}")
    
    nonsilent_parts = detect_nonsilent(audio_segment, min_silence_len=1000, silence_thresh=silence_thresh, seek_step=chunk_size)
    if nonsilent_parts:
        start_trim = nonsilent_parts[0][0]
        end_trim = nonsilent_parts[-1][1]
        logger.debug(f"Trimming from {start_trim}ms to {end_trim}ms")
        return audio_segment[start_trim:end_trim]
    logger.debug("No silence detected, returning original segment.")
    return audio_segment

class MergeMP3Thread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, audio_files, output_file, silence_thresh=-50.0, chunk_size=10, log_file=None):
        super().__init__()
        self.audio_files = audio_files
        self.output_file = output_file
        self.silence_thresh = silence_thresh
        self.chunk_size = chunk_size
        self.log_file = log_file

    def run(self):
        logger.info(f"Starting merge process for {len(self.audio_files)} files.")
        logger.info(f"Output file: {self.output_file}")
        logger.info(f"Log file: {self.log_file}")
        logger.info(f"Silence threshold: {self.silence_thresh}dBFS, Chunk size: {self.chunk_size}ms")

        try:
            combined = AudioSegment.empty()
            total_files = len(self.audio_files)
            current_time = 0
            self.progress.emit(0)

            log_entries = []
            for i, audio_file in enumerate(self.audio_files):
                logger.debug(f"Processing file {i+1}/{total_files}: {audio_file.path}")
                audio = AudioSegment.from_file(audio_file.path)
                audio = remove_silence(audio, silence_thresh=self.silence_thresh, chunk_size=self.chunk_size)
                combined += audio

                log_entries.append(f"{self.format_time(math.ceil(current_time / 1000))} {audio_file.display_name}")
                current_time += len(audio)

                self.progress.emit(int((i + 1) / total_files * 99))

            logger.info(f"Exporting merged file to {self.output_file}")
            combined.export(self.output_file, format='mp3', bitrate='256k')

            if self.log_file:
                logger.info(f"Writing log to {self.log_file}")
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    for entry in log_entries:
                        f.write(entry + '\n')
            
            self.progress.emit(100)
            logger.info("Merge process finished successfully.")
        except Exception as e:
            logger.error(f"An error occurred during the merge process: {e}", exc_info=True)


    @staticmethod
    def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        else:
            return f"{int(minutes):02}:{int(seconds):02}"