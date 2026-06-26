import common.utils.OSSUtils as ossUtils
class FileService:
    def uploadVoiceFile(self, fileName: str):
        return ossUtils.uploadSystemFileToOSS(fileName)

fileService = FileService()
