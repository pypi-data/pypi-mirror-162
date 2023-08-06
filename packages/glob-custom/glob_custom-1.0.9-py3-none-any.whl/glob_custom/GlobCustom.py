import glob
import os


class GlobCustom:
   def find_files_into_directory(self):
      """Собирает необходимые файлы из заданной дирректории"""
      self.glob_list = glob.glob(f"{self.directory}{self.pattern}{self.type_file}")
      return self.glob_list

   def remove_file_into_dir(self, function):
      """Удаляет файлы"""
      try:
         for file in self.glob_list:
            os.remove(file)
            print(f"{file} - удален")
      except:
         print(Exception)

   def remove_custom(self, directory, pattern='\*', type_file='.xlsx'):
      """Удаляет файлы в заданной дирректории"""
      self.directory = directory
      self.pattern = pattern
      self.type_file = type_file
      self.remove_file_into_dir(self.find_files_into_directory())
