import os
import shutil
import tempfile
import time

from win32com import client as win32


class AspenConnection(object):
    def __init__(self, file_path):
        self._aspen_original_file_path = file_path

        # Temporary folder verification
        parent_folder = tempfile.gettempdir() + "\\PWC Metadata"
        if not os.path.isdir(parent_folder):  # if directory doesn't exists, create it
            try:
                os.mkdir(parent_folder)
            except OSError:
                raise IOError("The metadata folder was not found and its creation attempt failed. Connection failed.")

        self._create_temp_folder(parent_folder)
        self._create_temp_aspen_copy()
        self._open_connection()

        # initialize temporary files
        self._temp_files_list = []

    def __del__(self):
        """
        Object destructor.
        """

        # close aspen connection
        self._close_connection(self._aspen)

        # clean up other files from temp dir
        os.remove(self._aspen_temp_file_path)  # temporary .bkp file

        for file in self._temp_files_list:  # generated text files
            file.close()

        # attempt to remove the folder with a 5 sec delay to allow unlock of the folder from the os
        try:
            shutil.rmtree(self._temp_directory)
        except WindowsError:
            time.sleep(5.0)
            shutil.rmtree(self._temp_directory, ignore_errors=True)

    def _create_temp_folder(self, parent_folder):
        # create a temporary directory to place the bkp copy file in there
        self._temp_directory = tempfile.mkdtemp(prefix='pwctmp', dir=parent_folder)

    def _create_temp_aspen_copy(self):
        # copy the file
        self._aspen_temp_file_path = os.path.join(self._temp_directory, 'pwc_temp.bkp')
        shutil.copy2(self._aspen_original_file_path, self._aspen_temp_file_path)

    def _create_temp_text_file(self, prefix):
        temp = tempfile.NamedTemporaryFile(mode='w+t', dir=self._temp_directory, prefix=prefix.replace('\\', '_'))
        self._temp_files_list.append(temp)

        return temp

    def _open_connection(self):
        self._aspen = win32.Dispatch('Apwn.Document')
        self._aspen.InitFromArchive2(os.path.abspath(self._aspen_temp_file_path))

    def _close_connection(self, connection_handle):
        while True:
            try:
                connection_handle.Close()
            except:
                break

    def _traverse_branch(self, node, file_to_write, level=0):
        if node.Dimension == 1 and hasattr(node, 'Elements'):  # node is might be a branch

            if node.Elements.count == 0:  # node is truly a leaf
                file_to_write.writelines('{0}{1} = {2} -- ({3}.L)\n'.format(' ' * level, node.Name, node.Value,
                                                                            level - 1))
            else:  # node is a branch with children
                file_to_write.writelines('{0}{1} -- ({2}.B)\n'.format(' ' * level, node.Name, level))
                for o in node.Elements:
                    self._traverse_branch(o, file_to_write, level + 1)

        else:
            file_to_write.writelines('{0}{1} = {2} -- ({3}.L)\n'.format(' ' * level, node.Name, node.Value,
                                                                        level - 1))

    def GetConnectionObject(self):
        """
        Returns the aspen object connection reference

        Returns
        -------
        CDispatch
            COMObject Apwn.Document
        """

        return self._aspen

    def GetTemporaryFolderPath(self):
        """
        Returns the string of the temporary folder path

        Returns
        -------
        string
            Directory file path
        """
        return self._temp_directory

    def GenerateTreeFile(self, branch_str):
        # create the txt file
        temp_txt = self._create_temp_text_file(branch_str)

        # traverse the tree and write results
        self._traverse_branch(self._aspen.Tree.FindNode(branch_str), temp_txt)

        temp_txt.seek(0)  # reset the file pointer
        return temp_txt

    def GetListofTextFilesDescriptors(self):
        """
        Returns the list of temporary file descriptors.

        Returns
        -------

        """
        return self._temp_files_list

    def ClearAllTextData(self):
        for file in self._temp_files_list:
            file.close()
