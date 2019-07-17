import os
import sys
import settings
from pathlib import Path
from contextlib import contextmanager

preamble = r'''
\documentclass{article}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}

\begin{document}
'''

postamble = r'''
\end{document}
'''

@contextmanager
def cd(path):
    oldpath = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(oldpath)

def main(args):
    outfile = settings.FIG_DIR / Path(args[0]).with_suffix('.tex')
    compilation_dir = outfile.parent

    tex_snippets = [
        '''
        \\includegraphics[width=0.3\\textwidth]{{{}}}

        '''.format(p)
        for p in args[1:]
    ]

    out_text = preamble + ''.join(tex_snippets) + postamble

    with open(outfile, 'w') as texout:
        texout.write(out_text)
    
    with cd(compilation_dir):
        os.system('pdflatex {}'.format(outfile))
        os.remove(outfile)
        os.remove(outfile.with_suffix('.aux'))
        os.remove(outfile.with_suffix('.log'))


    

if __name__ == "__main__":
    main(sys.argv[1:])

