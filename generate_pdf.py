__author__ = 'vlad'

import urllib.request
import pdfkit
import subprocess

def gethtml():
    r = urllib.request.urlopen("http://127.0.0.1:5000/print")
    bytecode = r.read()
    htmlstr = bytecode.decode()
    return htmlstr


def getpdf():
    pdfkit.from_string(gethtml(), "out.pdf")


def signpdf():
    subprocess.call(["java", "-jar", "/usr/local/PortableSigner/PortableSigner.jar", "-n",
                     "-t", "out.pdf",
                     "-o", "signed.pdf",
                     "-s", "sert.p12",
                     "-p", "1"])

if __name__ == "__main__":
    gethtml()
    getpdf()
    signpdf()






