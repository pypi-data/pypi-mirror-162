import sys
import threading

import sparknlp_jsl.internal as _internal
import sparknlp.internal as _internal_opensource
import threading
import time
from py4j.protocol import Py4JJavaError

def printProgress(stop):
    states = [' | ', ' / ', ' — ', ' \\ ']
    nextc = 0
    while True:
        sys.stdout.write('\r[{}]'.format(states[nextc]))
        sys.stdout.flush()
        time.sleep(2.5)
        nextc = nextc + 1 if nextc < 3 else 0
        if stop():
            sys.stdout.write('\r[{}]'.format('OK!'))
            sys.stdout.flush()
            break

    sys.stdout.write('\n')
    return


class InternalResourceDownloader(object):


    @staticmethod
    def downloadModel(reader, name, language, remote_loc=None, j_dwn='InternalsPythonResourceDownloader'):
        print(name + " download started this may take some time.")
        stop_threads = False
        t1 = threading.Thread(target=printProgress, args=(lambda: stop_threads,))
        t1.start()
        try:
                j_obj = _internal_opensource._DownloadModel(reader.name, name, language, remote_loc, j_dwn).apply()
        except Py4JJavaError as e:
                sys.stdout.write("\n" + str(e))
                raise e
        finally:
                stop_threads = True
                t1.join()

        return reader(classname=None, java_model=j_obj)

    @staticmethod
    def showPrivateModels(annotator=None, lang=None, version=None):
        print(_internal._ShowPrivateModels(annotator, lang, version).apply())

    @staticmethod
    def showPrivatePipelines(lang=None, version=None):
        print(_internal._ShowPrivatePipelines(lang, version).apply())

    @staticmethod
    def showUnCategorizedResources():
        print(_internal._ShowUnCategorizedResources().apply())

    @staticmethod
    def showAvailableAnnotators():
        print(_internal._ShowAvailableAnnotators().apply())

