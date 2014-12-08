#ifndef __CINT__
#include "RooGlobalFunc.h"
#endif
#include "RooStats/SPlot.h"
#include "TMath.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooTruthModel.h"
#include "RooExponential.h"
#include "RooResolutionModel.h"
#include "RooGaussModel.h"
#include "RooCBShape.h"
#include "RooAddModel.h"
#include "RooAbsPdf.h"
#include "RooAddPdf.h"
#include "RooHistPdf.h"
#include "RooProdPdf.h"
#include "RooDecay.h"
#include "TCanvas.h"
#include "TTree.h"
#include "TCut.h"
#include "TFile.h"
#include "RooPlot.h"
#include "TAxis.h"
//#include "JStyle.h"
#include <string>
#include "RooDataHist.h"
//#include "ksfun.h"
#include "TSystem.h"
#include "RooFitResult.h"
#include "TLatex.h"
#include "TH1.h"
#include <string>
#include <sstream>
#include <utility>

using namespace RooFit ;

// value + error 
typedef struct {

  float value;
  float error;
  
} ValueWithError;


// struct for binned result
typedef struct {

   ValueWithError sfrac;
   ValueWithError taub;
   ValueWithError sigma;
   ValueWithError mean;  

} BResult;

// struct for unbinned result
typedef struct {

   ValueWithError nsig;
   ValueWithError nback;
   ValueWithError taub;
   ValueWithError sigma;
   ValueWithError mean;  
   int status;
   int covQual;
   double norm;

} UBResult;


// struct for unbinned result


typedef struct {

   ValueWithError nsig;
 
   ValueWithError s1;
   ValueWithError s2;

   ValueWithError fb1;
   ValueWithError fb2;
   ValueWithError fb3;

   ValueWithError beta;
   ValueWithError taubacks;
   ValueWithError taubackl;
   int status; 

} BackResult;



typedef struct {

   ValueWithError nsig;
   ValueWithError nback;
   ValueWithError nsigtail;
  
   ValueWithError sigma;
   ValueWithError mean;  
   int status;
   int covQual;
  
   ValueWithError s1;
   ValueWithError s2;
   ValueWithError beta;
   ValueWithError taub;
   ValueWithError fb;
   ValueWithError taubacks;
   ValueWithError taubackl;
   double corelation;
   

} ResultTUB;





// helper for filling the structs
void fillValueWithError(ValueWithError* val,RooRealVar* var){
  val->value = var->getVal();
  val->error = var->getError();
}

// branch names
const std::string ptBranch = "X_PT";
const std::string etaBranch = "X_Y";
const std::string pBranch = "X_P";
const std::string massBranch = "X_M";

// fit range
const double maxmass = 3200.;//3786.;
const double minmass = 3000.;//3586;
const std::string mString =  "&& X_M > 3000 && X_M <3200 ";
const std::string bString =  "&& TMath::Abs(m-3686) > 60 ";

void addBlurb(TCanvas* can, double x, double y){

   std::cout << "Adding blurb to " << can->GetName() << std::endl; 

  TLatex *myLatex = new TLatex(0.5,0.5,"");
  myLatex->SetTextFont(132); 
  myLatex->SetTextColor(1); 
  myLatex->SetTextSize(0.045); 
  myLatex->SetNDC(kTRUE); 
  myLatex->SetTextAlign(11);  
  myLatex->SetTextSize(0.04); 
  myLatex->DrawLatex(x, y,"#splitline{LHCb Preliminary}{#scale[1]{#sqrt{s} = 8 TeV, L =18.4 pb^{-1}}}"); 
   
}


void addKineText(TCanvas* can, double x, double y, std::string ptMin = "0", std::string ptMax = "20000", 
                 std::string etaMin = "0", std::string etaMax = "10"){

  std::cout << "Adding kine info to " << can->GetName() << std::endl; 

  TLatex *myLatex = new TLatex(0.5,0.5,"");
  myLatex->SetTextFont(132); 
  myLatex->SetTextColor(1); 
  myLatex->SetTextSize(0.04); 
  myLatex->SetNDC(kTRUE); 
  myLatex->SetTextAlign(11);  
  myLatex->SetTextSize(0.045);

  stringstream ptminstream;  ptminstream << ptMin;
  double ptminval; ptminstream >> ptminval;
  stringstream ptmaxstream;  ptmaxstream << ptMax;
  double ptmaxval; ptmaxstream >> ptmaxval;
  int v1 = ptminval/1000.; 
  int v2 = ptmaxval/1000;
 

  std::string line1 = etaMin + " < y < " + etaMax;
  std::stringstream line2;  line2 << v1 << " < p_{T} < " << v2 << " [GeV/c]";
  std::string totstring = "#splitline{" + line1 + "}" + "{" + line2.str() +  "}";

  myLatex->DrawLatex(x, y, totstring.c_str()); 

}

// signal model - crystal ball with radiative tail fixed based on MC param
RooCBShape* signalModel(RooRealVar& mean, RooRealVar& s,  RooRealVar& n, RooRealVar& x, RooFormulaVar* tail, std::string name = "crystalball", std::string title = "cb(x,mean,sigma)" ){
  n.setConstant(true);
  return new RooCBShape(name.c_str(), title.c_str(),x, mean,s,*tail,n);
}

RooFormulaVar* tailModel(RooRealVar& s,RooRealVar& a0, RooRealVar& a1, RooRealVar& a2) {

  a0.setConstant(true);
  a1.setConstant(true);
  a2.setConstant(true);

  return new RooFormulaVar("a", "a",  "a0 + a1*sqrt(sigma*sigma) + a2*sigma*sigma",  RooArgSet(a0, a1, a2,  s));  
}

RooFormulaVar* tailModel2(RooRealVar& s,RooRealVar& a0, RooRealVar& a1, RooRealVar& a2) {

  a0.setConstant(true);
  a1.setConstant(true);
  a2.setConstant(true);

  return new RooFormulaVar("a", "a",  "a0 + a1*sqrt(sigma2*sigma2) + a2*sigma2*sigma2",  RooArgSet(a0, a1, a2,  s));  
}


// Guess the signal sigma based on p [in GeV !]
double expectedSigma(double p){
  return 1.2*(10.5 + p*0.06); 
}

std::pair<double, double> yield(TTree* theTree, std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin = "0", 
                               std::string etaMax = "10") {

 TCanvas* tCan = new TCanvas("tt","tt", 800., 600.);
   TH1F* h1 = new TH1F("histo", "histo", 100, 2900, 3300); h1->SetMinimum(0);
   TH1F* h2 = new TH1F("bhisto", "bhisto", 100, 2900, 3300); h2->SetMinimum(0);
  TH1F* h3 = new TH1F("bhisto2", "bhisto2", 100, 2900, 3300); h3->SetMinimum(0);

   std::string sigCutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax + 
                              "&&m > 3056.4 && m < 3137.4" ; 
   
   std::string backCutString1 = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax + 
     "&&m > 3000 && m <3041" ; 
    std::string backCutString2 = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax + 
     "&&m > 3169 && m <3210" ; 
   
   
   theTree->Draw("m >> histo",  sigCutString.c_str());
   theTree->Draw("m >> bhisto", backCutString1.c_str() );
   theTree->Draw("m >> bhisto2", backCutString2.c_str() );

   double tyield =  h1->GetEntries() - h2->GetEntries() - h3->GetEntries(); 
   double eyield = sqrt(pow(sqrt(h1->GetEntries()), 2) +pow(sqrt(h2->GetEntries()+h3->GetEntries()), 2)  );
   // std::cout << tyield << eyield << std::endl;
  return std::make_pair(tyield,eyield);

}


// binned fit
BResult binnedFit(TTree* theTree, std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin = "0", 
                  std::string etaMax = "10") {

  TCanvas* theCan = new TCanvas("tt","tt", 800., 600.);
  std::cout << "making canvas" << theCan->GetName() << std::endl;

  TH1F* h = new TH1F("histo", "histo", 100, minmass, maxmass);
  h->SetMinimum(0);
  TH1F* ph = new TH1F("phisto", "phisto", 200, 0., 100e3);


  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax +                          mString ;

  TCut theCut = cutString.c_str(); 
  std::cout << theCut << std::endl;

  // file the histogram
  theTree->Draw("X_M >> histo", theCut);
  theTree->Draw("X_PT >> phisto", theCut);
  BResult bresult;  

  TCanvas* can1 = new TCanvas("vv", "vv", 800,600);
  //h->Draw();

  RooRealVar x("x","x",minmass, maxmass);  

  RooRealVar taub("taub","taub",-0.001, -0.5,0.5);
  // RooRealVar taub("taub","taub",1e-10, -0.5,0.5);
  //taub.setConstant(true);
  RooExponential bg("back","exp",x,taub);

  RooRealVar mean("mean", "Mean", 3100, 3000., 3200.);
  RooRealVar s("sigma", "sigma", expectedSigma(ph->GetMean()/1000), -1., 50);
  RooRealVar a0("a0", "a0", 2.0118, -10, 10);
  RooRealVar a1("a1", "a1", 0.0102 , -10, 10);
  RooRealVar a2("a2", "a2", -0.0001845 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, x,tail);


  RooRealVar fsig("fsignal","signal fraction", 0.45, 0., 1.);
  RooAddPdf model("model","model", RooArgList(*cb,bg),fsig);

  RooDataHist data("data", "dataset", x, h);
  model.fitTo(data, NumCPU(2)); 

  TCanvas* can2 = new TCanvas("xx", "xx", 800,600);
  RooPlot* xframe = x.frame();
  data.plotOn(xframe);
  model.plotOn(xframe,Components("crystalball"), LineColor(kRed), LineStyle(2));
  model.plotOn(xframe,Components(bg.GetName()), LineColor(kGreen), LineStyle(2));
  model.plotOn(xframe);
  xframe->Draw();
  
  fillValueWithError(&(bresult.taub), &taub);
  fillValueWithError(&(bresult.mean), &mean);
  fillValueWithError(&(bresult.sigma), &s);
  fillValueWithError(&(bresult.sfrac), &fsig);

  return bresult;
}  

  
// unbinned fit
UBResult unbinnedFit(TTree* theTree, TCanvas* can, int pad, std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin = "0", 
		     std::string etaMax = "10", bool addParam = false) {

 
  UBResult uresult;

  BResult bresult = binnedFit(theTree, ptMin, ptMax, etaMin, etaMax);
  std::cout << bresult.mean.value << " "  <<  bresult.sigma.value << " " <<  bresult.taub.value << std::endl;

  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax +                          mString ; 
 
  TCut theCut = cutString.c_str(); 
  std::cout << theCut << std::endl;


  RooRealVar m("X_M","X_M",minmass, maxmass);  
  RooRealVar p("X_P","X_P",0, 500e3);  
  RooRealVar pt(ptBranch.c_str(),ptBranch.c_str(),0 , 100e3);  
  RooRealVar y("X_Y","X_Y",0, 10);  

  RooDataSet data("data","data",RooArgSet(m,p,pt,y),Import(*theTree),Cut(theCut)) ;
  int ntot = data.numEntries();

   RooRealVar taub("taub","taub",bresult.taub.value, -0.5,0.5); 
  //RooRealVar taub("taub","taub",1e-10, -0.5,0.5);
  //taub.setConstant(true);
  RooExponential bg("back","exp",m,taub);

  RooRealVar mean("mean", "Mean",
                  bresult.mean.value,
                  bresult.mean.value -40*bresult.mean.error,
                  bresult.mean.value +40*bresult.mean.error);
  RooRealVar s("sigma", "sigma",
               bresult.sigma.value,
               bresult.sigma.value - 40*bresult.sigma.error,
               bresult.sigma.value +40*bresult.sigma.error);
  RooRealVar a0("a0", "a0", 2.0118, -10, 10);
  RooRealVar a1("a1", "a1", 0.0102 , -10, 10);
  RooRealVar a2("a2", "a2", -0.0001845 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, m,tail);

  RooRealVar nsig("nsignal","n signal fraction",
                  bresult.sfrac.value*ntot, 0., ntot);
  RooRealVar nback("nback","n signal fraction",
                   (1-bresult.sfrac.value)*ntot, 0.,ntot);

  RooAddPdf model("model","model",
                  RooArgList(*cb,bg),
                  RooArgList(nsig,nback));

  RooFitResult* result =  model.fitTo(data, Extended(), Save(), NumCPU(2)); 
  if (pad != 0) {
   can->cd(pad);
  }
  else {
    can->cd();
  }

  RooPlot* xframe = m.frame();
  data.plotOn(xframe, Binning(44));
  model.plotOn(xframe,Components("crystalball"), LineColor(kRed), LineStyle(2));
  model.plotOn(xframe,Components(bg.GetName()), LineColor(kGreen), LineStyle(2));
  model.plotOn(xframe);
  if (addParam) model.paramOn(xframe); 
 
  // make it pretty
  xframe->SetXTitle("m_{#mu #mu } [MeV/c^{2}]");
  // xframe->SetYTitle("Candidates per 6 MeV/c^{2}");
  xframe->SetTitle("");
   
  TAxis* xachse = xframe->GetXaxis(); TAxis* yachse = xframe->GetYaxis();
   // mean.plotOn(xframe);
   xachse->SetTitleFont (132);
   yachse->SetTitleFont (132);
   xachse->SetLabelFont (132);
   yachse->SetLabelFont (132); 
   yachse->SetTitleOffset(1.2);

   // put everything on the canvas
  xframe->Draw();
  addBlurb(can,0.6,0.8);
  addKineText(can, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );


  // output the result  
  fillValueWithError(&(uresult.taub), &taub);
  fillValueWithError(&(uresult.mean), &mean);
  fillValueWithError(&(uresult.sigma), &s);
  fillValueWithError(&(uresult.nsig), &nsig);
  fillValueWithError(&(uresult.nback), &nback);
  uresult.covQual = result->covQual();
  uresult.status = result->status();
  
  RooRealVar m2("m2","m2",2200, maxmass);  
  RooRealVar mean2("mean", "mean2", mean.getVal());
  RooRealVar s2("sigma", "sigma", s.getVal() );
  RooFormulaVar* tail2 = tailModel(s2, a0, a1, a2);
  RooCBShape* cb2 = signalModel(mean2,s2,n, m2,tail2,"cb2");

  m2.setRange("signal",minmass, maxmass) ;
  RooAbsReal* igx_sig = cb2->createIntegral(m2,NormSet(m2),Range("signal")) ;
  std::cout << "Signal "<< igx_sig->getVal() <<  std::endl;
  uresult.norm =  igx_sig->getVal() ;
  //std::cout << uresult.norm << std::endl;

  return uresult;
}  

// unbinned fit
UBResult unbinnedSignalFit(TTree* theTree, TCanvas* can, int pad, std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin = "0", 
		     std::string etaMax = "10", bool addParam = false) {

 
  UBResult uresult;


  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax +                          mString ; 
 
  TCut theCut = cutString.c_str(); 
  std::cout << theCut << std::endl;


  RooRealVar m("X_M","X_M",minmass, maxmass);  
  RooRealVar p("X_P","X_P",0, 500e3);  
  RooRealVar pt(ptBranch.c_str(),ptBranch.c_str(),0 , 100e3);  
  RooRealVar y("yX_Y","X_Y",0, 10);  

  RooDataSet data("data","data",RooArgSet(m,p,pt,y),Import(*theTree),Cut(theCut)) ;
  // int ntot = data.numEntries();

  //RooRealVar taub("taub","taub",bresult.taub.value, -0.5,0.5); 
  // RooExponential bg("back","exp",m,taub);

  RooRealVar mean("mean", "Mean", 3099., 3090, 3110 );// mean.setConstant(true);
  RooRealVar s("sigma", "sigma", 10, 0, 50);
  RooRealVar a0("a0", "a0", 1.975, -10, 10);
  RooRealVar a1("a1", "a1", 0.011 , -10, 10);
  RooRealVar a2("a2", "a2", -0.00018 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, m,tail);

  //  RooRealVar nsig("nsignal","n signal fraction", bresult.sfrac.value*ntot, 0., ntot);
  //RooRealVar nback("nback","n signal fraction", (1-bresult.sfrac.value)*ntot, 0.,ntot);
  
 

  //  RooAddPdf model("model","model", RooArgList(*cb,bg),RooArgList(nsig,nback));

  RooFitResult* result =  cb->fitTo(data, Save(), NumCPU(2)); 
  if (pad != 0) {
   can->cd(pad);
  }
  else {
    can->cd();
  }

  RooPlot* xframe = m.frame();
  data.plotOn(xframe, Binning(44));
  cb->plotOn(xframe, LineColor(kRed), LineStyle(1));
  // model.plotOn(xframe,Components(bg.GetName()), LineColor(kGreen), LineStyle(2));
  // model.plotOn(xframe);
  if (addParam) cb->paramOn(xframe); 
 
  // make it pretty
  xframe->SetXTitle("m_{#mu #mu } [MeV/c^{2}]");
  // xframe->SetYTitle("Candidates per 6 MeV/c^{2}");
  xframe->SetTitle("");
   
  TAxis* xachse = xframe->GetXaxis(); TAxis* yachse = xframe->GetYaxis();
   // mean.plotOn(xframe);
   xachse->SetTitleFont (132);
   yachse->SetTitleFont (132);
   xachse->SetLabelFont (132);
   yachse->SetLabelFont (132); 
   yachse->SetTitleOffset(1.2);

   // put everything on the canvas
  xframe->Draw();
  addBlurb(can,0.6,0.8);
  addKineText(can, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );


  // output the result  
  //  fillValueWithError(&(uresult.taub), &taub);
  fillValueWithError(&(uresult.mean), &mean);
  fillValueWithError(&(uresult.sigma), &s);
  // fillValueWithError(&(uresult.nsig), &nsig);
  //  fillValueWithError(&(uresult.nback), &nback);
  // uresult.covQual = result->covQual();
  uresult.status = result->status();
  
  
  return uresult;
}  






// unbinned fit
UBResult unbinnedFitD(TTree* theTree, TCanvas* can, int pad, std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin = "0", 
		     std::string etaMax = "10", bool addParam = false) {

 
  UBResult uresult;

  BResult bresult = binnedFit(theTree, ptMin, ptMax, etaMin, etaMax);
  std::cout << bresult.mean.value << " "  <<  bresult.sigma.value << " " <<  bresult.taub.value << std::endl;

  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax +                          mString ; 
 
  TCut theCut = cutString.c_str(); 
  std::cout << theCut << std::endl;


  RooRealVar m("m","m",minmass, maxmass);  
  RooRealVar p("p","p",0, 500e3);  
  RooRealVar pt(ptBranch.c_str(),ptBranch.c_str(),0 , 100e3);  
  RooRealVar y("y","y",0, 10);  

  RooDataSet data("data","data",RooArgSet(m,p,pt,y),Import(*theTree),Cut(theCut)) ;
  int ntot = data.numEntries();

  RooRealVar taub("taub","taub",bresult.taub.value, -0.25,0.25); 
  RooExponential bg("back","exp",m,taub);

  RooRealVar mean("mean", "Mean", bresult.mean.value,bresult.mean.value -40*bresult.mean.error , bresult.mean.value +40*bresult.mean.error);
  RooRealVar s("sigma", "sigma", bresult.sigma.value, 5, 30 );
  RooRealVar s2("sigma2", "sigma2", 2*bresult.sigma.value, 5, 60 );
  RooRealVar f("f", "f", 0.8, 0, 1 );
  RooRealVar a0("a0", "a0", 1.975, -10, 10);
  RooRealVar a1("a1", "a1", 0.011 , -10, 10);
  RooRealVar a2("a2", "a2", -0.00018 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, m,tail);
  RooFormulaVar* tail2 = tailModel2(s2, a0, a1, a2);
  RooCBShape* cb2 = signalModel(mean,s2,n, m,tail2 , "cb2");

  RooAddPdf sigmodel("sigmodel","sigmodel",RooArgList(*cb,*cb2), f);

  RooRealVar nsig("nsignal","n signal fraction", bresult.sfrac.value*ntot, 0., ntot);
  RooRealVar nback("nback","n signal fraction", (1-bresult.sfrac.value)*ntot, 0.,ntot);
  
 

  RooAddPdf model("model","model", RooArgList(sigmodel,bg),RooArgList(nsig,nback));

  RooFitResult* result =  model.fitTo(data, Extended(), Save(), NumCPU(2)); 
  if (pad != 0) {
   can->cd(pad);
  }
  else {
    can->cd();
  }

  RooPlot* xframe = m.frame();
  data.plotOn(xframe, Binning(44));
  model.plotOn(xframe,Components(sigmodel.GetName()), LineColor(kRed), LineStyle(2));
  model.plotOn(xframe,Components(bg.GetName()), LineColor(kGreen), LineStyle(2));
  model.plotOn(xframe);
  if (addParam) model.paramOn(xframe); 
 
  // make it pretty
  xframe->SetXTitle("m_{#mu #mu } [MeV/c^{2}]");
  // xframe->SetYTitle("Candidates per 6 MeV/c^{2}");
  xframe->SetTitle("");
   
  TAxis* xachse = xframe->GetXaxis(); TAxis* yachse = xframe->GetYaxis();
   // mean.plotOn(xframe);
   xachse->SetTitleFont (132);
   yachse->SetTitleFont (132);
   xachse->SetLabelFont (132);
   yachse->SetLabelFont (132); 
   yachse->SetTitleOffset(1.2);

   // put everything on the canvas
  xframe->Draw();
  addBlurb(can,0.6,0.8);
  addKineText(can, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );


  // output the result  
  fillValueWithError(&(uresult.taub), &taub);
  fillValueWithError(&(uresult.mean), &mean);
  //  fillValueWithError(&(uresult.sigma), &s);
  
  double val = sqrt(f.getVal()*s.getVal()*s.getVal() + (1-f.getVal())*s2.getVal()*s2.getVal());
  uresult.sigma.value = val;
  uresult.sigma.error = 0.0;

  fillValueWithError(&(uresult.nsig), &nsig);
  fillValueWithError(&(uresult.nback), &nback);
  uresult.covQual = result->covQual();
  uresult.status = result->status();
  uresult.norm = 0;  

  /*
  RooRealVar m2("m2","m2",2200, maxmass);  
  RooRealVar mean2("mean", "mean2", mean.getVal());
  RooRealVar s3("sigma", "sigma", s.getVal() );
  RooFormulaVar* tail3 = tailModel(s2, a0, a1, a2);
  RooCBShape* cb3 = signalModel(mean2,s,n, m2,tail3,"cb3");

  m2.setRange("signal",minmass, maxmass) ;
  RooAbsReal* igx_sig = cb3->createIntegral(m2,NormSet(m2),Range("signal")) ;
  std::cout << "Signal "<< igx_sig->getVal() <<  std::endl;
  uresult.norm =  igx_sig->getVal() ;
  //std::cout << uresult.norm << std::endl;
  */
  return uresult;
}  


const double mJpsi = 3096.916;
const double C = 299792458000.0; 
// binned fit

TH1F* tzerrHisto(TTree* theTree, std::string cuts, std::string hname = "errHisto"){

  TH1F* h = new TH1F(hname.c_str(), hname.c_str(), 500, 0, 1);
  TCut theCut = cuts.c_str(); 
  std::string pipeString = "etz2 >>" + hname;
  theTree->Draw(pipeString.c_str(), theCut);
  return h;
}

TH1F* tzHisto(TTree* theTree, std::string cuts, std::string hname = "tzHisto"){

  TH1F* h = new TH1F(hname.c_str(), hname.c_str(), 100, -10, 10);
  TCut theCut = cuts.c_str(); 
  std::string pipeString = "tz2 >>" + hname;
  theTree->Draw(pipeString.c_str(), theCut);
  return h;
}



TH1F* tailHisto(TTree* theTree, double ptMin = 0, double ptMax = 20000, double etaMin = 0, 
		double etaMax = 10, std::string hname = "tailhisto") {

  std::cout << "processing " << ptMin << "  "<< ptMax << " " << etaMin << " " << etaMax << std::endl;

  double vz[5];
  

  TH1F* h = new TH1F(hname.c_str(), hname.c_str(), 400, -100, 100);
  double pt; theTree->SetBranchAddress("pt",&pt); 
  double y; theTree->SetBranchAddress("y",&y); 
  double zPrimary; theTree->SetBranchAddress("zPrimary",&zPrimary); 
  double zv; theTree->SetBranchAddress("zv",&zv); 
  theTree->SetBranchAddress("vz1",&vz[0]); 
  theTree->SetBranchAddress("vz2",&vz[1]); 
  theTree->SetBranchAddress("vz3",&vz[2]); 
  theTree->SetBranchAddress("vz4",&vz[3]); 
  theTree->SetBranchAddress("vz5",&vz[4]); 

  double PZ; theTree->SetBranchAddress("PZ",&PZ );  
  double event; theTree->SetBranchAddress("event",&event);
  // unsigned int run; theTree->SetBranchAddress("run",&run);

  int num_entries = theTree->GetEntries();
  //  std::cout << num_entries << std::endl;
  for (int i = 0; i <num_entries ; ++i){
    theTree->GetEntry(i);
    int oldevent = int(event);
    if (pt < ptMin || pt> ptMax) continue;
    if (y < etaMin || y > etaMax) continue;
    double zOld = zv;
    double OPZ  = PZ;
    for ( int j = i+10; j <num_entries && j < i+ 13  ; ++j ) {
       theTree->GetEntry(j);
       if (oldevent != int(event)){
         double dz = 9999;
         for (unsigned int i = 0; i < 5;++i){
	   double dztest = zOld - vz[i];
	   //  std::cout << dztest << " " << dz << std::endl; 
           if (TMath::Abs(dztest) < TMath::Abs(dz)) dz = dztest;  
	 }
	 //std::cout << " picked dz " << dz << std::endl;
         double tz = 1e12 * dz * mJpsi/(OPZ*C);
         h->Fill(tz);
       }
    }
   

  } // i

  // h->Draw();
  return h;
}  



ResultTUB tzmatt(TTree* theTree, TCanvas* tCan, TCanvas* tCan3 ,
                 int pad, TH1F* tHisto,  std::string ptMin = "0",
                 std::string ptMax = "20000", std::string etaMin = "0", 
                 std::string etaMax = "10"){


  ResultTUB timeResult;
 
  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax + mString ;
 
  stringstream ptminstream;  ptminstream << ptMin;
  double ptval; ptminstream >> ptval;
  
  stringstream etaminstream;  etaminstream << etaMin;
  double etaval; etaminstream >> etaval;
  

  // the phase space for the measurement
  RooRealVar m(massBranch.c_str(), massBranch.c_str(), minmass, maxmass);  
  RooRealVar p(pBranch.c_str(), pBranch.c_str(), 0, 500e3);  
  RooRealVar pt(ptBranch.c_str(), ptBranch.c_str(),0 , 100e3);  
  RooRealVar y(etaBranch.c_str(), etaBranch.c_str(), 0, 10);  
  RooRealVar tz2("X_TZ","X_TZ",-10, 10);
  RooRealVar etz2("etz2", "etz2", 0, 1);

  // the cuts 
  std::cout << " get data " << std::endl;
  TCut theCut = cutString.c_str(); 
  RooDataSet data("data", "data",
                  RooArgSet(m,p,pt,y,tz2), Import(*theTree), Cut(theCut)) ;
  int ntot = data.numEntries();
  std::cout << "Selected3 " << ntot << std::endl;

  BResult bresult = binnedFit(theTree, ptMin, ptMax, etaMin, etaMax);

  
  // the tail histo
  RooDataHist* tail_hist = new RooDataHist("tail_hist","tail_hist", tz2,tHisto);  
  RooHistPdf tail_pdf("tail_pdf","tail_pdf",tz2,*tail_hist) ;


  // signal resolution model
  RooRealVar *bkg_mean = new RooRealVar("bkg_mean","bias bkg",-2e-3,  -0.015, 0.015); //bkg_mean->setConstant(true);
  
  double sig_guess_s1 =  0.05 ;
  double sig_guess_s2 =  0.09; 
  RooRealVar *sig_s1 = new RooRealVar("sig_s1","sig_s1",sig_guess_s1, 0.02, 0.08);
  RooRealVar *sig_s2 = new RooRealVar("sig_s2","sig_s2", sig_guess_s2,  0.04, 0.16);
  RooRealVar *sbeta1 = new RooRealVar("sbeta1","sbeta1",0.8,  0, 1);
  RooResolutionModel *res_s1 = new RooGaussModel("res_s1","gauss resolution model part 1", tz2,*bkg_mean,*sig_s1);
  RooResolutionModel *res_s2 = new RooGaussModel("res_s2","gauss resolution model part 2", tz2,*bkg_mean,*sig_s2);
  RooAddModel *sig_gauss = new RooAddModel("sig_gauss","proper time for sig gauss", RooArgList(*res_s1, *res_s2), RooArgList(*sbeta1) );


  //background resolution model [double gauss]
  double bkg_guess_s1 =  0.6e-02 ;
  double bkg_guess_s2 =  0.16; 
  RooRealVar *bkg_s1 = new RooRealVar("bkg_s1","bkg_s1",bkg_guess_s1, 0.001, 0.08);
  RooRealVar *bkg_s2 = new RooRealVar("bkg_s2","bkg_s2", bkg_guess_s2,  0.003, 0.2);
  RooRealVar *beta1 = new RooRealVar("beta1","beta1",0.74,  0, 1);
  RooResolutionModel *res_b1 = new RooGaussModel("res_b1","gauss resolution model part 1", tz2,*bkg_mean,*bkg_s1);
  RooResolutionModel *res_b2 = new RooGaussModel("res_b2","gauss resolution model part 2", tz2,*bkg_mean,*bkg_s2);
  RooAddModel *bkg_gauss = new RooAddModel("bkg_gauss","proper time for bkg gauss", RooArgList(*res_s1, *res_s2), RooArgList(*beta1) );


  // exponential background (single sided)
  RooRealVar *bkg_taul = new RooRealVar("bkg_taul","bkg2_taul",1.2 , 0.8, 1.8); bkg_taul->setConstant(true);
  RooAbsPdf  *bkg_expl = new RooDecay("bkg_expl","bkg_expl", tz2, *bkg_taul, *bkg_gauss, RooDecay::SingleSided); 

  // exponential (double sided)
  RooRealVar *bkg_taus = new RooRealVar("bkg_taus","bkg_taus",0.2,  0.1, 0.5);  bkg_taus->setConstant(true);
  RooAbsPdf  *bkg_exps = new RooDecay("bkg_exps","bkg_exps", tz2, *bkg_taus, *bkg_gauss, RooDecay::DoubleSided); 


  // exponential (double sided -long and free)
  RooRealVar *bkg_taus2 = new RooRealVar("bkg_taus2","bkg_taus2",0.9,  0.6, 1.2 ); 
  RooAbsPdf  *bkg_exps2 = new RooDecay("bkg_exps2","bkg_exps2", tz2, *bkg_taus2, *bkg_gauss, RooDecay::DoubleSided); 



  // add them together....
  RooRealVar *fb1 = new RooRealVar("fb1","fb1",0.86,  0, 1);
  RooRealVar *fb2 = new RooRealVar("fb2","fb2",0.02,  0, 0.2);
  RooRealVar *fb3 = new RooRealVar("fb3","fb3",0.09,  0, 0.2);


  RooAbsPdf *bkg_tot = new RooAddPdf("bkg_tot","bkg_tot",RooArgList(*bkg_gauss,*bkg_expl,*bkg_exps,*bkg_exps2), RooArgList(*fb1,*fb2,*fb3));

  // mass pdf for background
  RooRealVar mtaub("mtaub","mtaub",bresult.taub.value,bresult.taub.value-10*bresult.taub.error , bresult.taub.value+10*bresult.taub.error); 
  RooExponential bgmass("backmass","expmass",m,mtaub);

  // combined pdf
  RooProdPdf *bkg = new RooProdPdf("bkg", "bkg", RooArgSet(bgmass, *bkg_tot));
  
  
  // mass pdf for signal
  RooRealVar mean("mean", "Mean", bresult.mean.value,bresult.mean.value -10*bresult.mean.error , bresult.mean.value +10*bresult.mean.error);
  RooRealVar s("sigma", "sigma", bresult.sigma.value, bresult.sigma.value - 10*bresult.sigma.error, bresult.sigma.value +10*bresult.sigma.error );
  RooRealVar a0("a0", "a0", 1.975, -10, 10);
  RooRealVar a1("a1", "a1", 0.011 , -10, 10);
  RooRealVar a2("a2", "a2", -0.00018 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, m,tail);

  // exponential background (single sided)
  double guessl = 1.4 - (0.02*ptval/1000.0);
  RooRealVar *sig_taul = new RooRealVar("sig_taul","sig_taul", guessl,  0.8, 1.8);  
  RooAbsPdf  *sig_expl = new RooDecay("sig_expl","sig_expl", tz2, *sig_taul, *bkg_gauss, RooDecay::SingleSided); 

  // total time pdf 
  double bfrac_guess = 0.05 + 0.012*ptval/1000. + ( 4.0 - etaval)*0.02 ;
  RooRealVar *fs1 = new RooRealVar("fs1","fs1",1-bfrac_guess,  0, 1);
  std::cout << "Guess "<< bfrac_guess << std::endl;
  RooAbsPdf *sig_tot = new RooAddPdf("sig_tot","sig_tot",RooArgList(*sig_gauss,*sig_expl), *fs1);

  // combined pdf for signal
  RooProdPdf *sig = new RooProdPdf("sig", "sig", RooArgSet(*cb, *sig_tot));
  
  // signal/tail pdf
  RooProdPdf *sigtail = new RooProdPdf("sigtail", "sigtail", RooArgSet(*cb, tail_pdf));
 
  // back/tail pdf
  RooProdPdf *backtail = new RooProdPdf("backtail", "backtail", RooArgSet(bgmass, tail_pdf));
 
  RooRealVar nsig("nsignal","n signal fraction", bresult.sfrac.value*ntot, bresult.sfrac.value*ntot - 20*sqrt(bresult.sfrac.value*ntot), bresult.sfrac.value*ntot + 20*sqrt(bresult.sfrac.value*ntot) );
  RooRealVar nback("nback","n back fraction", (1-bresult.sfrac.value)*ntot,  (1-bresult.sfrac.value)*ntot - 20*sqrt((1-bresult.sfrac.value)*ntot) , (1-bresult.sfrac.value)*ntot + 20*sqrt((1-bresult.sfrac.value)*ntot) );
  RooRealVar nsigtail("nsignaltail","n signal tail", bresult.sfrac.value*ntot/300., 0.,2000);
  RooRealVar nbacktail("nbacktail","n back tail", (1-bresult.sfrac.value)*ntot/300., 0.,4000);

  // for low entry bins..
  if (nback.getVal() < 100){
    fb1->setVal(0); fb1->setConstant(true);
    fb2->setVal(0); fb2->setConstant(true);
    bkg_taul->setConstant(true);
    beta1->setVal(0.0); beta1->setConstant(true);
    bkg_s2->setVal(0.0); bkg_s2->setConstant(true);   
    bkg_s1->setVal(0.0); bkg_s1->setConstant(true);
  }
  if (nsigtail.getVal() < 1.0){
    nsigtail.setVal(0);
    nsigtail.setConstant(true);
  }
  if (nbacktail.getVal() < 1.0){
    nbacktail.setVal(0);
    nbacktail.setConstant(true);
  }


  bool tofit = false;
  if (bresult.sfrac.value*ntot > 100) tofit = true;

  // RooRealVar *fsigt = new RooRealVar("fsigt","fsigt",0.99 ,  0, 1);
  if (tofit) {
    RooAbsPdf *tot = new RooAddPdf("totalFunction","totalFunction",RooArgList(*sig,*bkg,*sigtail, *backtail), RooArgList(nsig,nback , nsigtail , nbacktail));
    RooFitResult* theResult =0;
    //  theResult =  tot->fitTo(data, Extended(), Save(), NumCPU(2));

    // make the +/-4 sigma slice in mass for the plotting of t
    m.setRange("signalWindow", mean.getVal() - 4* s.getVal(), mean.getVal() + 4* s.getVal() );

    // the time plot
    //  TCanvas* tCan = new TCanvas("can2","can2", 800., 600.);
    if (pad != 0) {
      tCan->cd(pad);
      tCan->GetPad(pad)->SetLogy();
    }
    else {
      tCan->cd();
    }
    RooPlot* frametz = tz2.frame() ;
    frametz->SetTitle("");
    TAxis* xachse = frametz->GetXaxis(); TAxis* yachse = frametz->GetYaxis();
    xachse->SetTitleFont (132);
    yachse->SetTitleFont (132);
    xachse->SetLabelFont (132);
    yachse->SetLabelFont (132); 
    xachse->SetTitle("tz [ps]"); 
    yachse->SetTitle(" "); 
    data.plotOn(frametz, CutRange("signalWindow")) ;
    //  tot->plotOn(frametz);
    tot->plotOn(frametz,Components("sigtail"),LineColor(1), LineStyle(1), FillStyle(3008), FillColor(28), DrawOption("FL"), ProjectionRange("signalWindow") );
    tot->plotOn(frametz,Components("sigtail"),LineColor(38), ProjectionRange("signalWindow") );
    tot->plotOn(frametz,Components("bkg"),LineColor(3), LineStyle(1), FillStyle(3005), FillColor(3), DrawOption("FL") ,ProjectionRange("signalWindow") );
    tot->plotOn(frametz,Components("bkg"),LineColor(3), LineStyle(1), ProjectionRange("signalWindow"));
    tot->plotOn(frametz,Components("sig"),LineColor(1), LineStyle(1) ,ProjectionRange("signalWindow"));
    tot->plotOn(frametz, LineColor(2), ProjectionRange("signalWindow"));
    frametz->SetMinimum(0.2);
    tCan->SetLogy();
    frametz->Draw();
    addBlurb(tCan,0.6, 0.8);
    addKineText(tCan, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );

    // now the mass plot
    //  TCanvas* tCan3 = new TCanvas("can3","can3", 800., 600.);
    if (pad != 0) {
      tCan3->cd(pad);
    }
    else {
      tCan3->cd();
    }
    RooPlot* framem = m.frame() ;
    framem->SetTitle("");
    TAxis* xachse2 = framem->GetXaxis(); TAxis* yachse2 = framem->GetYaxis();
    xachse2->SetTitleFont (132);
    yachse2->SetTitleFont (132);
    xachse2->SetLabelFont (132);
    yachse2->SetLabelFont (132); 
    xachse2->SetTitle("tz [ps]"); 
    yachse2->SetTitle(" "); 
    data.plotOn(framem) ;
    tot->plotOn(framem,Components("bkg"),LineColor(3), LineStyle(2),FillColor(3), FillStyle(3005), DrawOption("F")  );
    tot->plotOn(framem,Components("bkg"),LineColor(3) );
    tot->plotOn(framem, LineColor(2));
    //framem->SetMinimum(1);
    framem->Draw();
    addBlurb(tCan3,0.6,0.8);
    addKineText(tCan3, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );


    // fill the stuff
    fillValueWithError(&(timeResult.mean), &mean);
    fillValueWithError(&(timeResult.sigma), &s);
    fillValueWithError(&(timeResult.nsig), &nsig);
    fillValueWithError(&(timeResult.nback), &nback);
    fillValueWithError(&(timeResult.nsigtail), &nsigtail);
    fillValueWithError(&(timeResult.s1), sig_s1);
    fillValueWithError(&(timeResult.s2), sig_s2);
    fillValueWithError(&(timeResult.beta), sbeta1);
    fillValueWithError(&(timeResult.fb), fs1);
    fillValueWithError(&(timeResult.taub), sig_taul);
    fillValueWithError(&(timeResult.taubacks), bkg_taus);
    fillValueWithError(&(timeResult.taubackl), bkg_taul);

    if (theResult){
      timeResult.covQual = theResult->covQual();
      timeResult.status = theResult->status();
      const TMatrixDSym& m = theResult->correlationMatrix();
      timeResult.corelation = m[6][13];
    }
    else {
      timeResult.covQual = -1;
      timeResult.status = -1;
      timeResult.corelation = 0;
    }
  }
  else {
    timeResult.covQual = -1;
    timeResult.status = -10;
    timeResult.corelation = 0;
  }

 return timeResult;
}



BackResult backfit(TTree* theTree, TCanvas* tCan,
                   int pad, TH1F* tHisto, std::string ptMin = "0",
                   std::string ptMax = "20000", std::string etaMin = "0", 
                   std::string etaMax = "10"){
  BackResult result;

  std::string cutString = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax + bString ; 
 
  // the phase space for the measurement
  RooRealVar m("m","m",minmass, maxmass);  
  RooRealVar p("p","p",0, 500e3);  
  RooRealVar pt(ptBranch.c_str(),ptBranch.c_str(),0 , 100e3);  
  RooRealVar y("y","y",0, 10);  
  RooRealVar tz2("tz2","tz2",-10, 10);  
  RooRealVar etz2("etz2", "etz2", 0, 1);

  // the cuts 
  std::cout << " get data " << std::endl;
  TCut theCut = cutString.c_str(); 
  //  RooDataSet data("data","data",RooArgSet(m,p,pt,y,tz2,etz2),Import(*theTree),Cut(theCut)) ;
  // int ntot = data.numEntries();

  TH1F* h = new TH1F("histo", "histo", 500, -10, 10); h->SetMinimum(0);  
  //TH1F* th = new TH1F("thisto", "thisto", 100, minmass, maxmass); th->SetMinimum(0);
  
  std::cout << theCut << " " << h->GetEntries() << std::endl;

  // file the histogram
  theTree->Draw("tz2 >> histo", theCut);
  // theTree->Draw("m >> thisto", theCut);
  //return;

  //  std::cout << "Selected " << ntot << std::endl;
  
  // the tail histo
  RooDataHist* tail_hist = new RooDataHist("tail_hist","tail_hist", tz2,tHisto);  
  RooHistPdf tail_pdf("tail_pdf","tail_pdf",tz2,*tail_hist) ;

  //background resolution model [double gauss]
  RooRealVar *bkg_mean = new RooRealVar("bkg_mean","bias bkg",0,  -0.05, 0.05); //bkg_mean->setConstant(true);
  double bkg_guess_s1 =  0.6e-02 ;
  double bkg_guess_s2 =  0.16; 
  RooRealVar *bkg_s1 = new RooRealVar("bkg_s1","bkg_s1",bkg_guess_s1, 0.002, 0.08);
  RooRealVar *bkg_s2 = new RooRealVar("bkg_s2","bkg_s2", bkg_guess_s2,  0.003, 0.2);
  RooRealVar *beta1 = new RooRealVar("beta1","beta1",0.74,  0.1, 1);
  RooResolutionModel *res_b1 = new RooGaussModel("res_b1","gauss resolution model part 1", tz2,*bkg_mean,*bkg_s1);
  RooResolutionModel *res_b2 = new RooGaussModel("res_b2","gauss resolution model part 2", tz2,*bkg_mean,*bkg_s2);
  RooAddModel *bkg_gauss = new RooAddModel("bkg_gauss","proper time for bkg gauss", RooArgList(*res_b1, *res_b2), RooArgList(*beta1) );

  // exponential background (single sided)
  RooRealVar *bkg_taul = new RooRealVar("bkg_taul","bkg2_taul",1.2,  0.1, 2.); bkg_taul->setConstant(true);
  RooAbsPdf  *bkg_expl = new RooDecay("bkg_expl","bkg_expl", tz2, *bkg_taul, *bkg_gauss, RooDecay::SingleSided); 

  // exponential (double sided)
  RooRealVar *bkg_taus = new RooRealVar("bkg_taus","bkg_taus",0.3,  0.1, 0.6 ); 
  RooAbsPdf  *bkg_exps = new RooDecay("bkg_exps","bkg_exps", tz2, *bkg_taus, *bkg_gauss, RooDecay::DoubleSided); 

  // exponential (double sided)
  RooRealVar *bkg_taus2 = new RooRealVar("bkg_taus2","bkg_taus2",0.6,  0.3, 1.0 ); 
  RooAbsPdf  *bkg_exps2 = new RooDecay("bkg_exps2","bkg_exps2", tz2, *bkg_taus2, *bkg_gauss, RooDecay::DoubleSided); 

  // add them together....
  RooRealVar *fb1 = new RooRealVar("fb1","fb1",0.9,  0, 1);
  RooRealVar *fb2 = new RooRealVar("fb2","fb2",0.02,  0, 1);
  RooRealVar *fb3 = new RooRealVar("fb3","fb3",0.99,  0, 1.0001);
  RooRealVar *fb4 = new RooRealVar("fb4","fb4",0.01,  0, 1.0001);


  RooAbsPdf *bkg_tot = new RooAddPdf("bkg_tot","bkg_tot",RooArgList(*bkg_gauss,*bkg_expl,*bkg_exps,*bkg_exps2), RooArgList(*fb1,*fb2,*fb4));

  // back/tail pdf
  //  RooRealVar nback("nback","n back fraction", 0.995*ntot, 0.,ntot);
  // RooRealVar nbacktail("nbacktail","n back tail", ntot*1e-3, 0.,1000);
  //   RooRealVar f("f","f", 0.99, 0.,1);


  RooAbsPdf* tot  =0;
  if (h->GetEntries() < 500){
    tot = bkg_tot;
  } else {
    RooAbsPdf *tot2 = new RooAddPdf("totalFunction","totalFunction",RooArgList(*bkg_tot, tail_pdf), *fb3);
    tot = tot2; 
  }
  //  RooAbsPdf *tot = new RooAddPdf("totalFunction","totalFunction",RooArgList(*bkg_tot, tail_pdf), RooArgList(nback ,nbacktail));
  RooFitResult* theResult =0;
  std::cout << "Fit " << std::endl;
  RooDataHist data("data", "dataset", tz2 , h); 
  theResult =  tot->fitTo(data, Save(), NumCPU(2), Save());
  if (theResult ==0) {
    result.status = -10;
    return result;
  }
  //  theResult =  tot->fitTo(data, Extended(), Save(), NumCPU(2));

    // the time plot
    //  TCanvas* tCan = new TCanvas("can2","can2", 800., 600.);
  if (pad != 0) {
    tCan->cd(pad);
    tCan->GetPad(pad)->SetLogy();
  }
  else {
    tCan->cd();
  }

  std::cout << "here " << std::endl;

  RooPlot* frametz = tz2.frame() ;
  frametz->SetTitle("");
  TAxis* xachse = frametz->GetXaxis(); TAxis* yachse = frametz->GetYaxis();
  xachse->SetTitleFont (132);
  yachse->SetTitleFont (132);
  xachse->SetLabelFont (132);
  yachse->SetLabelFont (132); 
  xachse->SetTitle("tz [ps]"); 
  yachse->SetTitle(" "); 

   data.plotOn(frametz);
  
   //  tot->plotOn(frametz,Components(),LineColor(3), LineStyle(1), FillStyle(3005), FillColor(3), DrawOption("FL")  );
   //tot->plotOn(frametz,Components("bkg_tot"),LineColor(3), LineStyle(1));  
  tot->plotOn(frametz, LineColor(2));
  frametz->SetMinimum(0.2);
  tCan->SetLogy();
  frametz->Draw();
  addBlurb(tCan,0.6, 0.8);
  addKineText(tCan, 0.15, 0.8, ptMin, ptMax, etaMin, etaMax );

   // fill the stuff
   fillValueWithError(&(result.s1), bkg_s1);
   fillValueWithError(&(result.s2), bkg_s2);
   fillValueWithError(&(result.beta), beta1);
   fillValueWithError(&(result.taubacks), bkg_taus);
   fillValueWithError(&(result.taubackl), bkg_taul);

   fillValueWithError(&(result.fb1), fb1); 
   fillValueWithError(&(result.fb2), fb2); 
   fillValueWithError(&(result.fb3), fb3); 
   result.status = theResult->status();

   delete theResult;
   std::cout << "fit completed" << std::endl;
   return result;
 
}

void SplitByBin(std::string inputFile = "input.root", std::string outFile = "selected.root", std::string ptMin = "0", std::string ptMax = "20000", std::string etaMin= "2", std::string etaMax = "4.5"){
 
 /*
   * Taking the data from the trees
   */

  TFile* datafile = new TFile(inputFile.c_str());         //creating a new TFile
  TTree* datatree = (TTree*)datafile->Get("tupleDimuon");        //selecting the correct branch from the root files 
  
  std::string cutstring = ptBranch + ">"  + ptMin  + "&&" + ptBranch + "<" +ptMax  + "&&"+ etaBranch  + ">" + etaMin + "&&" + etaBranch + "<" + etaMax ;                     
  TCut cut = cutstring.c_str();

  std::string dataSWeight = outFile.c_str();
  TFile* dataSWeight_out  = new TFile(outFile.c_str(),"RECREATE");
  TTree* dataSWtree = datatree->CopyTree(cut);

  TTree*  newDatatree = dataSWtree->CloneTree(-1);

  newDatatree->Write();
  dataSWeight_out->Close();
}

void addweights(std::string inputFile = "input.root", std::string outFile = "selected.root"){

  TFile* datafile = new TFile(inputFile.c_str());         
  TTree* datatree = (TTree*)datafile->Get("tupleDimuon");  

  BResult bresult = binnedFit(datatree);
  std::cout << bresult.mean.value << " "  <<  bresult.sigma.value << " " <<  bresult.taub.value << std::endl;


  RooRealVar m("m","m",minmass, maxmass);  
  RooRealVar p("p","p",0, 500e3);  
  RooRealVar pt(ptBranch.c_str(),ptBranch.c_str(),0 , 100e3);  
  RooRealVar y("y","y",0, 10);  

  RooDataSet data("data","data",RooArgSet(m,p,pt,y),Import(*datatree)) ;
  RooRealVar taub("taub","taub",bresult.taub.value, -0.5,0.5); 

  RooExponential bg("back","exp",m,taub);
  RooRealVar mean("mean", "Mean", bresult.mean.value,bresult.mean.value -40*bresult.mean.error , bresult.mean.value +40*bresult.mean.error);
  RooRealVar s("sigma", "sigma", bresult.sigma.value, bresult.sigma.value - 40*bresult.sigma.error, bresult.sigma.value +40*bresult.sigma.error );
  RooRealVar a0("a0", "a0", 2.0118, -10, 10);
  RooRealVar a1("a1", "a1", 0.0102 , -10, 10);
  RooRealVar a2("a2", "a2", -0.0001845 , -10, 10);
  RooRealVar n("n", "n", 1.0, 0, 10);
  RooFormulaVar* tail = tailModel(s, a0, a1, a2);
  RooCBShape* cb = signalModel(mean,s,n, m,tail);

  int ntot = data.numEntries();
  RooRealVar nsig("Nsig","n signal fraction", bresult.sfrac.value*ntot, 0., ntot);
  RooRealVar nback("Nbkg","n signal fraction", (1-bresult.sfrac.value)*ntot, 0.,ntot);
  
  RooAddPdf model("model","model", RooArgList(*cb,bg),RooArgList(nsig,nback));
  model.fitTo(data, Extended()); 

  TCanvas* tCan = new TCanvas("can","can", 800., 800.);
   

  RooStats::SPlot* sData = new RooStats::SPlot("sData","An SPlot", data, &model, RooArgList(nsig,nback)); 
  std::string dataSWeight = outFile.c_str();
  TFile* dataSWeight_out  = new TFile(outFile.c_str(),"RECREATE");
  
  TTree*  newtree = datatree->CloneTree(-1);
  
 float Nsig_sw; float Nbkg_sw; float Nsig2_sw; float Nref_sw;
 float  L_Nsig; float L_Nbkg;   float  L_Nsig2; float L_Nref;  
 TBranch*  b_Nsig_sw = newtree->Branch("Nsig_sw", &Nsig_sw,"Nsig_sw/F");  
 TBranch*  b_Nbkg_sw  = newtree->Branch("Nbkg_sw", &Nbkg_sw,"Nbkg_sw/F") ;
 TBranch*  b_L_Nsig  = newtree->Branch("L_Nsig", &L_Nsig,"L_Nsig/F") ;
 TBranch*  b_L_Nbkg = newtree->Branch("L_Nbkg", &L_Nbkg,"L_Nbkg/F") ; 

 for (int i = 0; i < data.numEntries(); ++i) {
   newtree->GetEntry(i);

   const RooArgSet* row = data.get(i); 
   Nsig_sw =  row->getRealValue("Nsig_sw");
   L_Nsig =  row->getRealValue("L_Nsig");
   Nbkg_sw =  row->getRealValue("Nbkg_sw");
   L_Nbkg =  row->getRealValue("L_Nbkg"); 
  
   b_Nsig_sw->Fill();
   b_L_Nsig->Fill();
   b_Nbkg_sw->Fill();
   b_L_Nbkg->Fill();

 }

  newtree->Write();
  dataSWeight_out->Close();


}
