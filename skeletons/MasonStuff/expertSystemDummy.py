from experta import *
from fpdf import FPDF


pdf = FPDF()

#Fact creation
class Leaf(Fact):
    pass

#Knowledge engine
class LeafIdentification(KnowledgeEngine):
    @Rule(Leaf(prognosis = "fine"))
    def noIssues(self):
        print("Leaf Doesn't Seem to Have any Issues")
        pdf.add_page()
        pdf.set_font("Times", size = 12)
        pdf.cell(200, 20, txt="This leaf appears to be healthy.\nDiagnosis: Paranoia", ln=True, align='C')
        pdf.output("diagnosis.pdf")
        print("Diagnostic generated successfully")

   # @Rule(Leaf("Disease1"))
   # def isdestroyed(self):

    @Rule(Leaf(prognosis="AphanomycesRootRot")) 
    def aphRot(self):
        print("Aphanomyces root rot")
        pdf.add_page()
        pdf.set_font("Times", size = 12)
        pdf.cell(200, 20, txt="Appears to have Aphanomyces root rot.", ln=True, align='C')
        pdf.output("diagnosis.pdf")
        print("Diagnostic generated successfully")
        
    @Rule(Leaf(prognosis="CassavaBlight"))
    def casBlight(self):
        print("Leaf has Aphanomyces root rot")
        pdf.add_page()
        pdf.set_font("Times", size = 12)
        pdf.cell(200, 20, txt="Appears to have Cassava Bacterial Blight.", ln=True, align='C')
        pdf.output("diagnosis.pdf")
        print("Diagnostic generated successfully")
        
#Engine creation

engine = LeafIdentification()
engine.reset()
#Potentially replace declarations with TensorFlow models
engine.declare(Leaf(prognosis="CassavaBlight")) 
engine.run() 