import os
from docutils.parsers.rst import Directive
from sphinx.writers.latex import LaTeXTranslator
from sphinx.util.osutil import copyfile

from docutils import nodes

class SideBySideDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()


        content_blocks = []
        content_offsets = []
        
        is_sep = [i=="&&" for i in self.content]+[True]
        N = sum(is_sep)
        frac = 0.999/N

        start = 0
        
        for i in range(N):
          stop = is_sep.index(True)
          is_sep[stop] = False
          content_blocks.append(self.content[start:stop])
          content_offsets.append(self.content_offset+start)
          start = stop+1
          

        local_nodes = []

        for content, offset in zip(content_blocks, content_offsets):
          text = '\n'.join(content)
          node = nodes.container(text)
          node['classes'].append('sidebyside')
          node.attributes['frac'] = str(frac)
          self.add_name(node)
          self.state.nested_parse(content, offset, node)
          local_nodes.append(node)


        node = nodes.container()
        node['classes'].append('sidebyside-master')
        node.extend(local_nodes)
        
        return [node]

class SideBySideLaTeXTranslator(LaTeXTranslator):
   def __init__(self, document, builder):
      LaTeXTranslator.__init__(self, document, builder)

   def visit_container(self, node):
      if 'sidebyside-master' in node["classes"]:
         self.body.append("\n")
      if 'sidebyside' in node["classes"]:
         self.body.append(r"\begin{minipage}[t]{%s\textwidth}" % node.attributes["frac"])

   def depart_container(self, node):
      if 'sidebyside-master' in node["classes"]:
         self.body.append("\n")
      if 'sidebyside' in node["classes"]:
         self.body.append(r"\end{minipage}"+"\n")

CSS_FILE = 'sidebyside.css'

def add_assets(app):
    try:
        app.add_stylesheet(CSS_FILE) # Deprecated
    except:
        app.add_css_file(CSS_FILE)


def copy_assets(app, exception):
    if 'html' not in app.builder.name or exception:
        return
    dest = os.path.join(app.builder.outdir, '_static', CSS_FILE)
    source = os.path.join(os.path.abspath(os.path.dirname(__file__)), CSS_FILE)
    copyfile(source, dest)


def setup(app):
    app.add_directive('side-by-side',  SideBySideDirective)
    app.set_translator('latex',  SideBySideLaTeXTranslator)

    app.connect('builder-inited', add_assets)
    app.connect('build-finished', copy_assets)

 
