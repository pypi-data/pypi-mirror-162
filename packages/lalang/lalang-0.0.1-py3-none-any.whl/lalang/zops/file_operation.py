# https://www.w3schools.com/python/python_ref_file.asp
# iden?F.../operation_choice
file_operation = """
file_operation:         penanda "F" file_operation_config? file_operation_choice

file_operation_config: fileoperationconfiglist "/"
fileoperationconfiglist: fileconfigitem+
fileconfigitem: "a" -> file_async_version
  | "A" -> file_sync_version

// with open(filepath, 'r') as identifier:

file_operation_choice: "n" filemodes? filepath -> create_file
  | "j>" expression_item -> json_out  // ?Fj>output = dumps/stringify/env, ?Fj<input = loads/parse/system
  | "j<" expression_item -> json_in
  | "1?" -> does_exist                // fs.existsSync(path)
  | "1!" -> does_not_exist            // !fs.existsSync(path)
  | "0?" -> is_empty
  | "d?" -> is_directory
  | "f?" -> is_regular_file // exist dan file
  | ">>" filepath -> write_string_to_file
  | ">>A" filepath -> write_list_to_file
  | "<<" filepath -> read_file_as_string
  | "<<A" filepath -> read_file_as_list
  | "<" -> fd_read_line
  | ">" -> fd_write_line
  | "o<" -> file_open_to_read         // fd = fs.openSync(path, "r")
  | "o>" -> file_open_to_write        // fd = fs.openSync(path, "w")
  | "00" -> fd_flush_file
  | ">0" -> fd_truncate_file
  | "." -> fd_close_file              // fd?F. = fs.closeSync(fd)
  | "@" -> fd_tell
  | "#" -> fd_fileno
  | "$" -> fd_seek
  | "-f" -> remove_file
  | "-f?" -> remove_file_if_exists
  | "-d" -> remove_directory
  | "-d?" -> remove_directory_if_exists
  | "+d" -> create_directory          // fs.mkdirSync(logDir)
  | "+d?" -> create_directory_if_doesnotexist

filemodes: filemode+
filemode: read_write_append
read_write_append: "w" -> write_mode // fd?Fnw'filename.txt'
  | "r" -> read_mode
  | "a" -> append_mode
  | "b" -> binary_mode
  | "d" -> directory_mode

filepath: literal_template_string
//| "*" -> get_content                // filecontent?F* = as_string
//| "*A" -> get_content_as_list       // filecontent?F*A
"""
