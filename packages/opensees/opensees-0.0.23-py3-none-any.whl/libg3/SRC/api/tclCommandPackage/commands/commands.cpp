// Written: cmp

// Description: This file contains the functions that will be called by
// the interpreter when the appropriate command name is specified.

#include <g3_api.h>
#include <G3_Runtime.h>
#include <G3_Logging.h>

#include <classTags.h>
#include <DOF_Group.h>

extern "C" {
#include <g3_api.h>
}

#include <OPS_Globals.h>
#include <Matrix.h>
#include <iostream>
#include <set>
#include <algorithm>

// the following is a little kludgy but it works!
#ifdef _USING_STL_STREAMS
#  include <iomanip>
   using std::ios;
#  include <iostream>
   using std::ofstream;
#else
#  include <StandardStream.h>
#  include <FileStream.h>
#  include <DummyStream.h>
   bool OPS_suppressOpenSeesOutput = false;
   bool OPS_showHeader = true;
/*
 * moved to streams/logging.cpp
   StandardStream sserr;
   OPS_Stream *opserrPtr = &sserr;
*/
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>

#include <elementAPI.h>
#include <g3_api.h>

#include <packages.h>
#include <TclPackageClassBroker.h>

#include <Timer.h>
#include <ModelBuilder.h>
#include "commands.h"

// domain
#ifdef _PARALLEL_PROCESSING
#  include <PartitionedDomain.h>
#else
#  include <Domain.h>
#endif

#include <Information.h>
#include <Element.h>
#include <Node.h>
#include <ElementIter.h>
#include <NodeIter.h>
#include <LoadPattern.h>
#include <LoadPatternIter.h>
#include <ElementalLoad.h>
#include <ElementalLoadIter.h>
#include <ParameterIter.h>
#include <SP_Constraint.h>     //Joey UC Davis
#include <SP_ConstraintIter.h> //Joey UC Davis
#include <MP_Constraint.h>
#include <MP_ConstraintIter.h>
#include <Parameter.h>
#include <ParameterIter.h>
#include <InitialStateParameter.h>
#include <ElementStateParameter.h>
#include <Pressure_Constraint.h>

// analysis model
#include <AnalysisModel.h>


// soln algorithms
#include <Linear.h>
#include <NewtonRaphson.h>
#include <NewtonLineSearch.h>
#include <ModifiedNewton.h>
#include <Broyden.h>
#include <BFGS.h>
#include <KrylovNewton.h>
#include <PeriodicNewton.h>
#include <AcceleratedNewton.h>
#include <ExpressNewton.h>

#include <StaticIntegrator.h>

// constraint handlers
#include <PlainHandler.h>
#include <PenaltyConstraintHandler.h>
//#include <PenaltyHandlerNoHomoSPMultipliers.h>
#include <LagrangeConstraintHandler.h>
#include <TransformationConstraintHandler.h>

// numberers
#include <PlainNumberer.h>
#include <DOF_Numberer.h>
// graph
#include <RCM.h>
#include <AMDNumberer.h>


#ifdef OPS_USE_PFEM
#include <PFEMIntegrator.h>
#endif

#include <Integrator.h> //Abbas

//  recorders
#include <Recorder.h> //SAJalali
#include <analysisAPI.h>


#include <Newmark.h>
#include <StagedNewmark.h>
#include <TRBDF2.h>
#include <TRBDF3.h>
#include <Newmark1.h>
#include <Houbolt.h>
#include <ParkLMS3.h>
#include <BackwardEuler.h>

// analysis
#include <StaticAnalysis.h>
#include <DirectIntegrationAnalysis.h>
#include <VariableTimeStepDirectIntegrationAnalysis.h>

#ifdef OPS_USE_PFEM
#  include <PFEMAnalysis.h>
#endif

// system of eqn and solvers
#include <BandSPDLinSOE.h>
#include <BandSPDLinLapackSolver.h>

#include <BandGenLinSOE.h>
#include <BandGenLinLapackSolver.h>

#include <ConjugateGradientSolver.h>

#ifdef _ITPACK
//#include <ItpackLinSOE.h>
//#include <ItpackLinSolver.h>
#endif

#include <FullGenLinSOE.h>
#include <FullGenLinLapackSolver.h>

#include <ProfileSPDLinSOE.h>
#include <ProfileSPDLinDirectSolver.h>
#include <DiagonalSOE.h>
#include <DiagonalDirectSolver.h>

#include <SProfileSPDLinSolver.h>
#include <SProfileSPDLinSOE.h>

// #include <ProfileSPDLinDirectBlockSolver.h>
// #include <ProfileSPDLinDirectThreadSolver.h>
// #include <ProfileSPDLinDirectSkypackSolver.h>
// #include <BandSPDLinThreadSolver.h>

#include <SparseGenColLinSOE.h>
#ifdef OPS_USE_PFEM
#  include <PFEMSolver.h>
#  include <PFEMSolver_Umfpack.h>
#  include <PFEMLinSOE.h>
#  include <PFEMCompressibleSolver.h>
#  include <PFEMCompressibleLinSOE.h>
#endif
#ifdef _MUMPS
#  include <PFEMSolver_Mumps.h>
#  include <PFEMCompressibleSolver_Mumps.h>
#endif

#ifdef _THREADS
#  include <ThreadedSuperLU.h>
#else
#  include <SuperLU.h>
#endif

#ifdef _CUSP
#  include <CuSPSolver.h>
#endif

#ifdef _CULAS4
#  include <CulaSparseSolverS4.h>
#endif

#ifdef _CULAS5
#  include <CulaSparseSolverS5.h>
#endif


#ifdef _PETSC
#  include <PetscSOE.h>
#  include <PetscSolver.h>
#  include <SparseGenRowLinSOE.h>
#  include <PetscSparseSeqSolver.h>
#endif

#include <SparseGenRowLinSOE.h>
#include <SymSparseLinSOE.h>
#include <SymSparseLinSolver.h>
#include <UmfpackGenLinSOE.h>
#include <UmfpackGenLinSolver.h>
#include <EigenSOE.h>
#include <EigenSolver.h>
#include <ArpackSOE.h>
#include <ArpackSolver.h>
#include <SymArpackSOE.h>
#include <SymArpackSolver.h>
#include <BandArpackSOE.h>
#include <BandArpackSolver.h>
#include <SymBandEigenSOE.h>
#include <SymBandEigenSolver.h>
#include <FullGenEigenSOE.h>
#include <FullGenEigenSolver.h>

#ifdef _CUDA
#  include <BandGenLinSOE_Single.h>
#  include <BandGenLinLapackSolver_Single.h>
#endif

#include <ErrorHandler.h>
#include <ConsoleErrorHandler.h>

#ifdef _NOGRAPHICS
// Do nothing
#else
#  include <TclVideoPlayer.h>
#endif

#include <FE_Datastore.h>

const char *getInterpPWD(Tcl_Interp *interp);

#include <XmlFileStream.h>
#include <Response.h>

ModelBuilder *theBuilder = 0;

// some global variables
#ifdef _PARALLEL_PROCESSING
#  include <DistributedDisplacementControl.h>
#  include <ShadowSubdomain.h>
#  include <Metis.h>
#  include <ShedHeaviest.h>
#  include <DomainPartitioner.h>
#  include <GraphPartitioner.h>
#  include <TclPackageClassBroker.h>
#  include <Subdomain.h>
#  include <SubdomainIter.h>
#  include <MachineBroker.h>
#  include <MPIDiagonalSOE.h>
#  include <MPIDiagonalSolver.h>
// parallel analysis
#  include <StaticDomainDecompositionAnalysis.h>
#  include <TransientDomainDecompositionAnalysis.h>
#  include <ParallelNumberer.h>

//  parallel soe & solvers
#  include <DistributedBandSPDLinSOE.h>
#  include <DistributedSparseGenColLinSOE.h>
#  include <DistributedSparseGenRowLinSOE.h>
#  include <DistributedBandGenLinSOE.h>
#  include <DistributedDiagonalSOE.h>
#  include <DistributedDiagonalSolver.h>

#  define MPIPP_H
#  include <DistributedSuperLU.h>
#  include <DistributedProfileSPDLinSOE.h>

// MachineBroker *theMachineBroker = 0;
   int  OPS_PARALLEL_PROCESSING = 0;
   int  OPS_NUM_SUBDOMAINS = 0;
   bool OPS_PARTITIONED = false;
   bool OPS_USING_MAIN_DOMAIN = false;
   bool setMPIDSOEFlag = false;
   int  OPS_MAIN_DOMAIN_PARTITION_ID = 0;
   PartitionedDomain     theDomain;
   DomainPartitioner     *OPS_DOMAIN_PARTITIONER = 0;
   GraphPartitioner      *OPS_GRAPH_PARTITIONER = 0;
   LoadBalancer          *OPS_BALANCER = 0;
   TclPackageClassBroker *OPS_OBJECT_BROKER = 0;
   MachineBroker         *OPS_MACHINE = 0;
   Channel               **OPS_theChannels = 0;  

#  elif defined(_PARALLEL_INTERPRETERS)

  bool setMPIDSOEFlag = false;
  
  // parallel analysis
  #include <ParallelNumberer.h>
  #include <DistributedDisplacementControl.h>
  
  //  parallel soe & solvers
  #include <DistributedBandSPDLinSOE.h>
  #include <DistributedSparseGenColLinSOE.h>
  #include <DistributedSparseGenRowLinSOE.h>
  
  #include <DistributedBandGenLinSOE.h>
  #include <DistributedDiagonalSOE.h>
  #include <DistributedDiagonalSolver.h>
  #include <MPIDiagonalSOE.h>
  #include <MPIDiagonalSolver.h>
  #define MPIPP_H
  #include <DistributedSuperLU.h>
  #include <DistributedProfileSPDLinSOE.h>
  Domain theDomain;
#else
  Domain theDomain;
#endif

#include <MachineBroker.h>


extern "C" int OPS_ResetInputNoBuilder(ClientData clientData,
                                       Tcl_Interp *interp, int cArg, int mArg,
                                       TCL_Char **argv, Domain *domain);

typedef struct parameterValues {
  char *value;
  struct parameterValues *next;
} OpenSeesTcl_ParameterValues;

typedef struct parameter {
  char *name;
  OpenSeesTcl_ParameterValues *values;
  struct parameter *next;
} OpenSeesTcl_Parameter;

typedef struct externalClassFunction {
  char *funcName;
  void *(*funcPtr)();
  struct externalClassFunction *next;
} ExternalClassFunction;
static ExternalClassFunction *theExternalSolverCommands = NULL;
static OpenSeesTcl_Parameter *theParameters = NULL;
static OpenSeesTcl_Parameter *endParameters = NULL;
static int numParam = 0;
static char **paramNames = 0;
static char **paramValues = 0;

MachineBroker *theMachineBroker = 0;
Channel **theChannels = 0;
int numChannels = 0;
int OPS_rank = 0;
int OPS_np = 0;

AnalysisModel *theAnalysisModel = 0;
EquiSolnAlgo *theAlgorithm = 0;
ConstraintHandler *theHandler = 0;
DOF_Numberer *theNumberer = 0;
LinearSOE *theSOE = 0;
EigenSOE *theEigenSOE = 0;
StaticAnalysis *theStaticAnalysis = 0;
DirectIntegrationAnalysis *theTransientAnalysis = 0;
VariableTimeStepDirectIntegrationAnalysis
    *theVariableTimeStepTransientAnalysis = 0;
int numEigen = 0;

#ifdef OPS_USE_PFEM
   static PFEMAnalysis *thePFEMAnalysis = 0;
#endif

StaticIntegrator *theStaticIntegrator = 0;
TransientIntegrator *theTransientIntegrator = 0;
ConvergenceTest *theTest = 0;
bool builtModel = false;

static char *resDataPtr = 0;
static int resDataSize = 0;
static Timer *theTimer = 0;

#include <FileStream.h>
#include <SimulationInformation.h>
SimulationInformation simulationInfo;
SimulationInformation *theSimulationInfoPtr = 0;

char *simulationInfoOutputFilename = 0;

FE_Datastore *theDatabase = 0;
TclPackageClassBroker theBroker;


#ifdef _NOGRAPHICS

#else
   TclVideoPlayer *theTclVideoPlayer = 0;
#endif

// g3AppInit() is the method called by tkAppInit() when the
// interpreter is being set up .. this is where all the
// commands defined in this file are registered with the interpreter.

int printModelGID(ClientData, Tcl_Interp *, int, TCL_Char **);
int printA(ClientData, Tcl_Interp *, int, TCL_Char **);
int printB(ClientData, Tcl_Interp *, int, TCL_Char **);

int setPrecision(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int logFile(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int version(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int getPID(ClientData,  Tcl_Interp *, int, TCL_Char **argv);
int getNP( ClientData,  Tcl_Interp *, int, TCL_Char **argv);
int opsBarrier(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int domainChange(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int record(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int opsSend(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int opsRecv(ClientData, Tcl_Interp *, int,TCL_Char **argv);
int opsPartition(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int peerNGA(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int defaultUnits(ClientData, Tcl_Interp *, int, TCL_Char **argv);
int stripOpenSeesXML(ClientData, Tcl_Interp *, int, TCL_Char **);
// int setParameter(ClientData, Tcl_Interp *, int, TCL_Char **);

// extern
int OpenSeesExit(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv);

extern int myCommands(Tcl_Interp *interp);

int
TclCommand_setLoadConst(ClientData, Tcl_Interp *, int, TCL_Char **);
int
TclCommand_getTime(ClientData, Tcl_Interp *, int, TCL_Char **);
int
TclCommand_setTime(ClientData, Tcl_Interp *, int, TCL_Char **);
int
TclCommand_setCreep(ClientData, Tcl_Interp *, int, TCL_Char **);

int convertBinaryToText(ClientData clientData, Tcl_Interp *interp, int argc,
                        TCL_Char **argv);

int convertTextToBinary(ClientData clientData, Tcl_Interp *interp, int argc,
                        TCL_Char **argv);

int maxOpenFiles(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv);

// pointer for old putsCommand

static Tcl_ObjCmdProc *Tcl_putsCommand = 0;

//
// revised puts command to send to cerr!
//
/*
int TclObjCommand_getRuntimeAddr(ClientData cd, Tcl_Interp *interp, int objc, Tcl_Obj *const objv[])
{
  Tcl_SetObjResult(interp, rt_str);
}
*/
int
OpenSees_putsCommand(ClientData dummy, Tcl_Interp *interp, int objc,
                     Tcl_Obj *const objv[])
{
  Tcl_Channel chan;           /* The channel to puts on. */
  Tcl_Obj *string;            /* String to write. */
  Tcl_Obj *chanObjPtr = NULL; /* channel object. */
  int newline;                /* Add a newline at end? */

  switch (objc) {
  case 2: /* [puts $x] */
    string = objv[1];
    newline = 1;
    break;

  case 3: /* [puts -nonewline $x] or [puts $chan $x] */
    if (strcmp(Tcl_GetString(objv[1]), "-nonewline") == 0) {
      newline = 0;
    } else {
      newline = 1;
      chanObjPtr = objv[1];
    }
    string = objv[2];
    break;

  case 4: /* [puts -nonewline $chan $x] or [puts $chan $x nonewline] */
    newline = 0;
    if (strcmp(Tcl_GetString(objv[1]), "-nonewline") == 0) {
      chanObjPtr = objv[2];
      string = objv[3];
      break;
    } else if (strcmp(Tcl_GetString(objv[3]), "nonewline") == 0) {
      /*
       * The code below provides backwards compatibility with an old
       * form of the command that is no longer recommended or
       * documented. See also [Bug #3151675]. Will be removed in Tcl 9,
       * maybe even earlier.
       */

      chanObjPtr = objv[1];
      string = objv[2];
      break;
    }
    /* Fall through */
  default:
    /* [puts] or [puts some bad number of arguments...] */
    Tcl_WrongNumArgs(interp, 1, objv, "?-nonewline? ?channelId? string");
    return TCL_ERROR;
  }

  if (chanObjPtr == NULL) {
    G3_Runtime* rt;
    if ((rt = G3_getRuntime(interp))) {
      if (newline == 0)
        fprintf(rt->streams[1], "%s", Tcl_GetString(string));
      else
        fprintf(rt->streams[1], "%s\n", Tcl_GetString(string));
    } else {
      if (newline == 0)
        opserr << Tcl_GetString(string);
      else
        opserr << Tcl_GetString(string) << endln;
    }
    return TCL_OK;
  } else {
    if (Tcl_putsCommand != 0) {
      return Tcl_putsCommand(dummy, interp, objc, objv);
    } else {
      opsmrd
          << "MEARD!  commands.cpp .. old puts command not found or set!\n";
      return TCL_ERROR;
    }
    return TCL_OK;
  }
}

int
Tcl_InterpOpenSeesObjCmd(ClientData clientData, Tcl_Interp *interp, int objc,
                         Tcl_Obj *CONST objv[])
{
  int index;
  static TCL_Char *options[] = {"alias",          "aliases",      "create",
                                "delete",         "eval",         "exists",
                                "expose",         "hide",         "hidden",
                                "issafe",         "invokehidden", "marktrusted",
                                "recursionlimit", "slaves",       "share",
                                "target",         "transfer",     NULL};
  enum option {
    OPT_ALIAS,
    OPT_ALIASES,
    OPT_CREATE,
    OPT_DELETE,
    OPT_EVAL,
    OPT_EXISTS,
    OPT_EXPOSE,
    OPT_HIDE,
    OPT_HIDDEN,
    OPT_ISSAFE,
    OPT_INVOKEHID,
    OPT_MARKTRUSTED,
    OPT_RECLIMIT,
    OPT_SLAVES,
    OPT_SHARE,
    OPT_TARGET,
    OPT_TRANSFER
  };

  int ok = TCL_OK;

  if (Tcl_GetIndexFromObj(interp, objv[1], options, "option", 0, &index) !=
      TCL_OK) {
    return TCL_ERROR;
  }

  switch ((enum option)index) {
  case OPT_CREATE: {
    TCL_Char *theInterpreterName = Tcl_GetStringResult(interp);
    Tcl_Interp *secondaryInterp = Tcl_GetSlave(interp, theInterpreterName);
    ok = OpenSeesAppInit(secondaryInterp);
    return ok;
    break;
  }
  default:
    return ok;
  }

  return ok;
}

int
OpenSeesAppInit(Tcl_Interp *interp)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);
  ops_TheActiveDomain = the_domain;

  //
  // redo puts command so we can capture puts into std:cerr
  //

  if (OPS_suppressOpenSeesOutput == false) {
    // get a handle on puts procedure
    Tcl_CmdInfo putsCommandInfo;
    Tcl_GetCommandInfo(interp, "puts", &putsCommandInfo);
    Tcl_putsCommand = putsCommandInfo.objProc;
    // if handle, use ouur procedure as opposed to theirs
    if (Tcl_putsCommand != 0) {
      Tcl_CreateObjCommand(interp, "oldputs", Tcl_putsCommand, NULL, NULL);
      Tcl_CreateObjCommand(interp, "puts", OpenSees_putsCommand, NULL, NULL);
    }
  }

  theSimulationInfoPtr = &simulationInfo;

#ifndef _LINUX
  opserr.setFloatField(SCIENTIFIC);
  opserr.setFloatField(FIXEDD);
#endif

  // Tcl_CreateObjCommand(interp, "interp", Tcl_InterpOpenSeesObjCmd, NULL,
  // NULL);

  Tcl_CreateCommand(interp, "recorderValue", &OPS_recorderValue,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL); // by SAJalali

  Tcl_CreateObjCommand(interp, "pset", &OPS_SetObjCmd, (ClientData)NULL,
                       (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateObjCommand(interp, "source", &OPS_SourceCmd, (ClientData)NULL,
                       (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "getNDM", &getNDM, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getNDF", &getNDF, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "wipe", &wipeModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "wipeAnalysis", &wipeAnalysis, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "reset", &resetModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "initialize", &initializeAnalysis, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "loadConst", &TclCommand_setLoadConst, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "setCreep", &TclCommand_setCreep, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setTime", &TclCommand_setTime, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getTime", &TclCommand_getTime, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getLoadFactor", &getLoadFactor, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "build", &buildModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "analyze", &analyzeModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "print", &printModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "printModel", &printModel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "printA", &printA, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "printB", &printB, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

// TODO: cmp -- reimplement
//   // Talledo Start
//   Tcl_CreateCommand(interp, "printGID", &printModelGID, (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
//   // Talledo End
  Tcl_CreateCommand(interp, "analysis", &specifyAnalysis, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "fault", 
      [](ClientData,Tcl_Interp*,int,const char **)->int{throw 20; return 0;}, 
        (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "system", &specifySysOfEqnTable, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "numberer", &specifyNumberer, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "constraints", &specifyConstraintHandler, nullptr, nullptr);
  Tcl_CreateCommand(interp, "algorithm", &specifyAlgorithm, (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "test", &specifyCTest, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "testNorms", &getCTestNorms, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "testIter", &getCTestIter, nullptr, nullptr);

  Tcl_CreateCommand(interp, "integrator", &specifyIntegrator, nullptr, nullptr);

  Tcl_CreateCommand(interp, "recorder", &addRecorder, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "algorithmRecorder", &addAlgoRecorder,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  
 //  Tcl_CreateCommand(interp, "database", &addDatabase, (ClientData)NULL,
 //                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "eigen", &eigenAnalysis, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "modalProperties", &modalProperties,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "responseSpectrum", &responseSpectrum,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "video", &videoPlayer, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "remove", &removeObject, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "eleForce", &eleForce, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "localForce", &localForce, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "eleDynamicalForce", &eleDynamicalForce,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "eleResponse", &eleResponse, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeDisp", &nodeDisp, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setNodeDisp", &setNodeDisp, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeReaction", &nodeReaction, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeUnbalance", &nodeUnbalance, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeEigenvector", &nodeEigenvector,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeVel", &nodeVel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setNodeVel", &setNodeVel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeAccel", &nodeAccel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setNodeAccel", &setNodeAccel, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeResponse", &nodeResponse, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "reactions", &calculateNodalReactions,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeDOFs", &nodeDOFs, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeCoord", &nodeCoord, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setNodeCoord", &setNodeCoord, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "updateElementDomain", &updateElementDomain,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "eleType", &eleType, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "eleNodes", &eleNodes, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeMass", &nodeMass, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodePressure", &nodePressure, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "nodeBounds", &nodeBounds, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "start", &startTimer, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "stop", &stopTimer, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "rayleigh", &rayleighDamping, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  // Tcl_CreateCommand(interp, "modalDamping", &modalDamping, (ClientData)NULL,
  //                   (Tcl_CmdDeleteProc *)NULL);
  // Tcl_CreateCommand(interp, "modalDampingQ", &modalDampingQ, (ClientData)NULL,
  //                   (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setElementRayleighDampingFactors",
                    &setElementRayleighDampingFactors, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "region", &addRegion, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "logFile", &logFile, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "setPrecision", &setPrecision, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "exit", &OpenSeesExit, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "quit", &OpenSeesExit, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "findNodeWithID", &findID, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "getNP", &getNP, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getPID", &getPID, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "barrier", &opsBarrier, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "send", &opsSend, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "recv", &opsRecv, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "partition", &opsPartition, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "searchPeerNGA", &peerNGA, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "domainChange", &domainChange, (ClientData)NULL,
                    NULL);

  Tcl_CreateCommand(interp, "record", &record, (ClientData)NULL, NULL);

  Tcl_CreateCommand(interp, "defaultUnits", &defaultUnits, (ClientData)NULL,
                    NULL);
  Tcl_CreateCommand(interp, "stripXML", &stripOpenSeesXML, (ClientData)NULL,
                    NULL);
  Tcl_CreateCommand(interp, "convertBinaryToText", &convertBinaryToText,
                    (ClientData)NULL, NULL);
  Tcl_CreateCommand(interp, "convertTextToBinary", &convertTextToBinary,
                    (ClientData)NULL, NULL);

  Tcl_CreateCommand(interp, "getEleTags", &getEleTags, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getNodeTags", &getNodeTags, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getParamTags", &getParamTags, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getParamValue", &getParamValue, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "fixedNodes", &fixedNodes, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "fixedDOFs", &fixedDOFs, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "constrainedNodes", &constrainedNodes,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "constrainedDOFs", &constrainedDOFs,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "retainedNodes", &retainedNodes, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "retainedDOFs", &retainedDOFs, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "getNumElements", &getNumElements, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getEleClassTags", &getEleClassTags,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getEleLoadClassTags", &getEleLoadClassTags,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getEleLoadTags", &getEleLoadTags, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "getEleLoadData", &getEleLoadData, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "sdfResponse", &sdfResponse, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "sectionForce", &sectionForce, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "sectionDeformation", &sectionDeformation,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "sectionStiffness", &sectionStiffness,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "sectionFlexibility", &sectionFlexibility,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "sectionLocation", &sectionLocation,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "sectionWeight", &sectionWeight, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "basicDeformation", &basicDeformation,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "basicForce", &basicForce, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "basicStiffness", &basicStiffness, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  // command added for initial state analysis for nDMaterials
  // Chris McGann, U.Washington
  Tcl_CreateCommand(interp, "InitialStateAnalysis", &InitialStateAnalysis,
                    (ClientData)NULL, (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "totalCPU", &totalCPU, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "solveCPU", &solveCPU, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "accelCPU", &accelCPU, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "numFact", &numFact, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "numIter", &numIter, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "systemSize", &systemSize, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);
  Tcl_CreateCommand(interp, "version", &version, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

//   TODO: cmp, moved definition to packages/optimization; need to link in optionally
//   Tcl_CreateCommand(interp, "setParameter", &setParameter, (ClientData)NULL,
//                     (Tcl_CmdDeleteProc *)NULL);

  Tcl_CreateCommand(interp, "setMaxOpenFiles", &maxOpenFiles, (ClientData)NULL,
                    (Tcl_CmdDeleteProc *)NULL);

  theAlgorithm = 0;
  theHandler = 0;
  theNumberer = 0;
  theAnalysisModel = 0;
  theSOE = 0;
  theStaticIntegrator = 0;
  theTransientIntegrator = 0;
  theStaticAnalysis = 0;
  theTransientAnalysis = 0;
  theVariableTimeStepTransientAnalysis = 0;
  theTest = 0;

  // create an error handler

  return myCommands(interp);
}

int
OPS_SetObjCmd(ClientData clientData, Tcl_Interp *interp, int objc,
              Tcl_Obj *const objv[])
{

  if (objc > 2)
    simulationInfo.addParameter(Tcl_GetString(objv[1]), Tcl_GetString(objv[2]));

  Tcl_Obj *varValueObj;

  if (objc == 2) {
    varValueObj = Tcl_ObjGetVar2(interp, objv[1], NULL, TCL_LEAVE_ERR_MSG);
    if (varValueObj == NULL) {
      return TCL_ERROR;
    }
    Tcl_SetObjResult(interp, varValueObj);
    return TCL_OK;
  } else if (objc == 3) {
    varValueObj =
        Tcl_ObjSetVar2(interp, objv[1], NULL, objv[2], TCL_LEAVE_ERR_MSG);
    if (varValueObj == NULL) {
      return TCL_ERROR;
    }
    Tcl_SetObjResult(interp, varValueObj);
    return TCL_OK;
  } else {
    Tcl_WrongNumArgs(interp, 1, objv, "varName ?newValue?");
    return TCL_ERROR;
  }

  return 0;
}

int
OPS_SourceCmd(ClientData dummy,      /* Not used. */
              Tcl_Interp *interp,    /* Current interpreter. */
              int objc,              /* Number of arguments. */
              Tcl_Obj *CONST objv[]) /* Argument objects. */
{
  CONST char *encodingName = NULL;
  Tcl_Obj *fileName;

  if (objc != 2 && objc != 4) {
    Tcl_WrongNumArgs(interp, 1, objv, "?-encoding name? fileName");
    return TCL_ERROR;
  }

  fileName = objv[objc - 1];

  if (objc == 4) {
    static CONST char *options[] = {"-encoding", NULL};
    int index;

    if (TCL_ERROR == Tcl_GetIndexFromObj(interp, objv[1], options, "option",
                                         TCL_EXACT, &index)) {
      return TCL_ERROR;
    }
    encodingName = Tcl_GetString(objv[2]);
  }

  const char *pwd = getInterpPWD(interp);
  const char *fileN = Tcl_GetString(fileName);

  simulationInfo.addInputFile(fileN, pwd);

#ifndef _TCL85
  return Tcl_EvalFile(interp, fileN);
#else
  return Tcl_FSEvalFileEx(interp, fileName, encodingName);
#endif
}

int
wipeModel(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  wipeAnalysis(clientData, interp, argc, argv);
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  // TclSafeBuilder *builder = G3_getSafeBuilder(rt);

  /*
  // to build the model make sure the ModelBuilder has been constructed
  // and that the model has not already been constructed
  if (theBuilder != 0) {
    delete theBuilder;
    builtModel = false;
    theBuilder = 0;
  }

  if (the_static_analysis != 0) {
      the_static_analysis->clearAll();
      delete the_static_analysis;
  }

  if (theTransientAnalysis != 0) {
      theTransientAnalysis->clearAll();
      delete theTransientAnalysis;
  }
  */

  // NOTE : DON'T do the above on theVariableTimeStepAnalysis
  // as it and theTansientAnalysis are one in the same
  if (theDatabase != 0)
    delete theDatabase;

  if (domain) {
    domain->clearAll();
  }

  // builder->clearAllUniaxialMaterial();
  // builder->clearAllNDMaterial();
  // builder->clearAllSectionForceDeformation();
  // OPS_clearAllHystereticBackbone(rt);
  // OPS_clearAllStiffnessDegradation(rt);
  // OPS_clearAllStrengthDegradation(rt);
  // OPS_clearAllUnloadingRule(rt);

  ops_Dt = 0.0;

#ifdef _PARALLEL_PROCESSING
  OPS_PARTITIONED = false;
#endif

  theAlgorithm = 0;
  theHandler = 0;
  theNumberer = 0;
  G3_setAnalysisModel(rt,nullptr);
  // theSOE = 0;
  G3_setLinearSoe(rt, nullptr);
  G3_setStaticIntegrator(rt,nullptr);
  theTransientIntegrator = 0;
  G3_setStaticAnalysis(rt,nullptr);
  theTransientAnalysis = 0;
  theVariableTimeStepTransientAnalysis = 0;

  theTest = 0;
  theDatabase = 0;

// AddingSensitivity:BEGIN /////////////////////////////////////////////////
#ifdef _RELIABILITY
  // theSensitivityAlgorithm =0;
  theSensitivityIntegrator = 0;
#endif
  // AddingSensitivity:END /////////////////////////////////////////////////

  // the domain deletes the record objects,
  // just have to delete the private array
  return TCL_OK;
}

int
wipeAnalysis(ClientData cd, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  StaticAnalysis* the_static_analysis = G3_getStaticAnalysis(rt);
  DirectIntegrationAnalysis* dia = G3_getTransientAnalysis(rt);

  if (the_static_analysis != 0) {
    the_static_analysis->clearAll();
    G3_delStaticAnalysis(rt);
  }

  if (dia != 0) {
    dia->clearAll();
    delete dia;
  }

  // NOTE : DON'T do the above on theVariableTimeStepAnalysis
  // as it and theTansientAnalysis are one in the same

  theAlgorithm = 0;
  theHandler   = 0;
  theNumberer  = 0;
  G3_setAnalysisModel(rt,nullptr);
  // theSOE = 0;
  G3_setLinearSoe(rt, nullptr);
  theEigenSOE = 0;
  G3_setStaticIntegrator(rt,nullptr);
  theTransientIntegrator = 0;
  G3_setStaticAnalysis(rt,nullptr);

  theTransientAnalysis = 0;
  G3_setTransientAnalysis(rt, nullptr);
  theVariableTimeStepTransientAnalysis = 0;
#ifdef OPS_USE_PFEM
  thePFEMAnalysis = 0;
#endif
  theTest = 0;

#ifdef _RELIABILITY
  // AddingSensitivity:BEGIN /////////////////////////////////////////////////
  theSensitivityAlgorithm = 0;
  theSensitivityIntegrator = 0;
  // AddingSensitivity:END /////////////////////////////////////////////////
#endif
  return TCL_OK;
}

// by SAJalali
int
OPS_recorderValue(ClientData clientData, Tcl_Interp *interp, int argc,
                  TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system

  // clmnID starts from 1
  if (argc < 3) {
    opserr << "WARNING want - recorderValue recorderTag clmnID <rowOffset> "
              "<-reset>\n";
    return TCL_ERROR;
  }

  int tag, rowOffset;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING recorderValue recorderTag? clmnID <rowOffset> <-reset> "
              "could not read recorderTag \n";
    return TCL_ERROR;
  }

  if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
    opserr << "WARNING recorderValue recorderTag? clmnID - could not read "
              "clmnID \n";
    return TCL_ERROR;
  }
  dof--;
  rowOffset = 0;
  int curArg = 3;
  if (argc > curArg) {
    if (Tcl_GetInt(interp, argv[curArg], &rowOffset) != TCL_OK) {
      opserr << "WARNING recorderValue recorderTag? clmnID <rowOffset> "
                "<-reset> could not read rowOffset \n";
      return TCL_ERROR;
    }
    curArg++;
  }
  bool reset = false;
  if (argc > curArg) {
    if (strcmp(argv[curArg], "-reset") == 0)
      reset = true;
    curArg++;
  }
  Recorder *theRecorder = domain->getRecorder(tag);
  double res = theRecorder->getRecordedValue(dof, rowOffset, reset);
  // now we copy the value to the tcl string that is returned
  // sprintf(interp->result, "%35.8f ", res);
  char buffer[40];
  sprintf(buffer, "%35.8f", res);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
resetModel(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  domain->revertToStart();

  if (theTransientIntegrator != 0) {
    theTransientIntegrator->revertToStart();
  }
  return TCL_OK;
}

int
initializeAnalysis(ClientData clientData, Tcl_Interp *interp, int argc,
                   TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  StaticAnalysis* the_static_analysis = G3_getStaticAnalysis(rt);
  
  if (theTransientAnalysis != 0) {
    DirectIntegrationAnalysis* ana;
    if (ana=G3_getTransientAnalysis(rt))
      ana->initialize();
    else
      theTransientAnalysis->initialize();
  } else if (the_static_analysis != 0) {
    the_static_analysis->initialize();
  }

  domain->initialize();

  return TCL_OK;
}



int
getLoadFactor(ClientData clientData, Tcl_Interp *interp, int argc,
              TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);

  if (argc < 2) {
    opserr << "WARNING no load pattern supplied -- getLoadFactor\n";
    return TCL_ERROR;
  }

  int pattern;
  if (Tcl_GetInt(interp, argv[1], &pattern) != TCL_OK) {
    opserr << "ERROR reading load pattern tag -- getLoadFactor\n";
    return TCL_ERROR;
  }

  LoadPattern *the_pattern = domain->getLoadPattern(pattern);
  if (the_pattern == 0) {
    opserr << "ERROR load pattern with tag " << pattern
           << " not found in domain -- getLoadFactor\n";
    return TCL_ERROR;
  }

  double factor = the_pattern->getLoadFactor();

  char buffer[40];
  sprintf(buffer, "%35.20f", factor);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}


// command invoked to build the model, i.e. to invoke buildFE_Model()
// on the ModelBuilder

int
buildModel(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  ModelBuilder* builder = (ModelBuilder*)G3_getModelBuilder(rt);
  if (!builder)
    builder = theBuilder;
  // TODO: Remove `builtModel` var.
  // to build the model make sure the ModelBuilder has been constructed
  // and that the model has not already been constructed
  if (builder != 0 && builtModel == false) {
    builtModel = true;
    return builder->buildFE_Model();
  } else if (builder != 0 && builtModel == true) {
    opserr << "WARNING Model has already been built - not built again \n";
    return TCL_ERROR;
  } else {
    opserr << "WARNING No ModelBuilder type has been specified \n";
    return TCL_ERROR;
  }
}


int
opsPartition(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
#ifdef _PARALLEL_PROCESSING
  int eleTag;
  if (argc == 2) {
    if (Tcl_GetInt(interp, argv[1], &eleTag) != TCL_OK) {
      ;
    }
  }
  partitionModel(eleTag);
#endif
  return TCL_OK;
}

//
// command invoked to build the model, i.e. to invoke analyze()
// on the Analysis object
//
int
analyzeModel(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  int result = 0;
  G3_Runtime *rt = G3_getRuntime(interp);
  StaticAnalysis* the_static_analysis = G3_getStaticAnalysis(rt);

  if (the_static_analysis != 0) {
    int numIncr;
    if (argc < 2) {
      opserr << "WARNING static analysis: analysis numIncr?\n";
      return TCL_ERROR;
    }

    if (Tcl_GetInt(interp, argv[1], &numIncr) != TCL_OK)
      return TCL_ERROR;

    result = the_static_analysis->analyze(numIncr);
#ifdef OPS_USE_PFEM
  } else if (thePFEMAnalysis != 0) {
    result = thePFEMAnalysis->analyze();
#endif
  } else if (theTransientAnalysis != 0) {
    double dT;
    int numIncr;
    if (argc < 3) {
      opserr << "WARNING transient analysis: analysis numIncr? deltaT?\n";
      return TCL_ERROR;
    }
    if (Tcl_GetInt(interp, argv[1], &numIncr) != TCL_OK)
      return TCL_ERROR;
    if (Tcl_GetDouble(interp, argv[2], &dT) != TCL_OK)
      return TCL_ERROR;

    // Set global timestep variable
    ops_Dt = dT;

    if (argc == 6) {
      int Jd;
      double dtMin, dtMax;
      if (Tcl_GetDouble(interp, argv[3], &dtMin) != TCL_OK)
        return TCL_ERROR;
      if (Tcl_GetDouble(interp, argv[4], &dtMax) != TCL_OK)
        return TCL_ERROR;
      if (Tcl_GetInt(interp, argv[5], &Jd) != TCL_OK)
        return TCL_ERROR;

      if (theVariableTimeStepTransientAnalysis != 0)
        result = theVariableTimeStepTransientAnalysis->analyze(
            numIncr, dT, dtMin, dtMax, Jd);
      else {
        opserr << "WARNING analyze - no variable time step transient analysis "
                  "object constructed\n";
        return TCL_ERROR;
      }

    } else {
      result = theTransientAnalysis->analyze(numIncr, dT);
    }

  } else {
    opserr << "WARNING No Analysis type has been specified \n";
    return TCL_ERROR;
  }

  if (result < 0) {
    opserr << "OpenSees > analyze failed, returned: " << result
           << " error flag\n";
  }

  char buffer[10];
  sprintf(buffer, "%d", result);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  //  sprintf(interp->result,"%d",result);

  return TCL_OK;
}


int
printAlgorithm(ClientData clientData, Tcl_Interp *interp, int argc,
               TCL_Char **argv, OPS_Stream &output)
{
  int eleArg = 0;
  if (theAlgorithm == 0)
    return TCL_OK;

  // if just 'print <filename> algorithm'- no flag
  if (argc == 0) {
    theAlgorithm->Print(output);
    return TCL_OK;
  }

  // if 'print <filename> Algorithm flag' get the flag
  int flag;
  if (Tcl_GetInt(interp, argv[eleArg], &flag) != TCL_OK) {
    opserr << "WARNING print algorithm failed to get integer flag: \n";
    opserr << argv[eleArg] << endln;
    return TCL_ERROR;
  }
  theAlgorithm->Print(output, flag);
  return TCL_OK;
}

int
printIntegrator(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv, OPS_Stream &output)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  StaticIntegrator *the_static_integrator = G3_getStaticIntegrator(rt);
  int eleArg = 0;
  if (the_static_integrator == 0 && theTransientIntegrator == 0)
    return TCL_OK;

  IncrementalIntegrator *theIntegrator;
  if (the_static_integrator != 0)
    theIntegrator = the_static_integrator;
  else
    theIntegrator = theTransientIntegrator;

  // if just 'print <filename> algorithm'- no flag
  if (argc == 0) {
    theIntegrator->Print(output);
    return TCL_OK;
  }

  // if 'print <filename> Algorithm flag' get the flag
  int flag;
  if (Tcl_GetInt(interp, argv[eleArg], &flag) != TCL_OK) {
    opserr << "WARNING print algorithm failed to get integer flag: \n";
    opserr << argv[eleArg] << endln;
    return TCL_ERROR;
  }
  theIntegrator->Print(output, flag);
  return TCL_OK;
}

int
printA(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int res = 0;

  FileStream outputFile;
  OPS_Stream *output = &opserr;
  LinearSOE *theSOE = *G3_getLinearSoePtr(G3_getRuntime(interp));

  bool ret = false;
  int currentArg = 1;
  while (currentArg < argc) {
    if ((strcmp(argv[currentArg], "file") == 0) ||
        (strcmp(argv[currentArg], "-file") == 0)) {
      currentArg++;

      if (outputFile.setFile(argv[currentArg]) != 0) {
        opserr << "print <filename> .. - failed to open file: "
               << argv[currentArg] << endln;
        return TCL_ERROR;
      }
      output = &outputFile;
    } else if ((strcmp(argv[currentArg], "ret") == 0) ||
               (strcmp(argv[currentArg], "-ret") == 0)) {
      ret = true;
    }
    currentArg++;
  }
  if (theSOE != 0) {
    if (theStaticIntegrator != 0)
      theStaticIntegrator->formTangent();
    else if (theTransientIntegrator != 0)
      theTransientIntegrator->formTangent(0);

    const Matrix *A = theSOE->getA();
    if (A != 0) {
      if (ret) {
        int n = A->noRows();
        int m = A->noCols();
        if (n * m > 0) {
          for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
              char buffer[40];
              sprintf(buffer, "%.10e ", (*A)(i, j));
              Tcl_AppendResult(interp, buffer, NULL);
            }
          }
        }
      } else {
        *output << *A;
        // close the output file
        outputFile.close();
      }
    }
  }

  return res;
}

int
printB(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int res = 0;

  FileStream outputFile;
  OPS_Stream *output = &opserr;
  //  bool done = false;

  bool ret = false;
  int currentArg = 1;
  while (currentArg < argc) {
    if ((strcmp(argv[currentArg], "file") == 0) ||
        (strcmp(argv[currentArg], "-file") == 0)) {
      currentArg++;

      if (outputFile.setFile(argv[currentArg]) != 0) {
        opserr << "print <filename> .. - failed to open file: "
               << argv[currentArg] << endln;
        return TCL_ERROR;
      }
      output = &outputFile;
    } else if ((strcmp(argv[currentArg], "ret") == 0) ||
               (strcmp(argv[currentArg], "-ret") == 0)) {
      ret = true;
    }
    currentArg++;
  }
  if (theSOE != 0) {
    if (theStaticIntegrator != 0)
      theStaticIntegrator->formUnbalance();
    else if (theTransientIntegrator != 0)
      theTransientIntegrator->formUnbalance();

    const Vector &b = theSOE->getB();
    if (ret) {
      int n = b.Size();
      if (n > 0) {
        for (int i = 0; i < n; i++) {
          char buffer[40];
          sprintf(buffer, "%.10e ", b(i));
          Tcl_AppendResult(interp, buffer, NULL);
        }
      }
    } else {
      *output << b;
      // close the output file
      outputFile.close();
    }
  }

  return res;
}


//
// command invoked to allow the Numberer objects to be built
//
int
specifyNumberer(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  // make sure at least one other argument to contain numberer
  if (argc < 2) {
    opserr << "WARNING need to specify a Numberer type \n";
    return TCL_ERROR;
  }

#ifdef _PARALLEL_PROCESSING
  // check argv[1] for type of Numberer and create the object
  if (strcmp(argv[1], "Plain") == 0) {
    theNumberer = new ParallelNumberer();
  } else if (strcmp(argv[1], "RCM") == 0) {
    RCM *theRCM = new RCM(false);
    theNumberer = new ParallelNumberer(*theRCM);
  } else {
    opserr << "WARNING No Numberer type exists (Plain, RCM only) \n";
    return TCL_ERROR;
  }
#else

  // check argv[1] for type of Numberer and create the object
  if (strcmp(argv[1], "Plain") == 0) {
    theNumberer = new PlainNumberer();
  } else if (strcmp(argv[1], "RCM") == 0) {
    RCM *theRCM = new RCM(false);
    theNumberer = new DOF_Numberer(*theRCM);
  } else if (strcmp(argv[1], "AMD") == 0) {
    AMD *theAMD = new AMD();
    theNumberer = new DOF_Numberer(*theAMD);
  }

#  ifdef _PARALLEL_INTERPRETERS

  else if ((strcmp(argv[1], "ParallelPlain") == 0) ||
           (strcmp(argv[1], "Parallel") == 0)) {
    ParallelNumberer *theParallelNumberer = new ParallelNumberer;
    theNumberer = theParallelNumberer;
    theParallelNumberer->setProcessID(OPS_rank);
    theParallelNumberer->setChannels(numChannels, theChannels);
  } else if (strcmp(argv[1], "ParallelRCM") == 0) {
    RCM *theRCM = new RCM(false);
    ParallelNumberer *theParallelNumberer = new ParallelNumberer(*theRCM);
    theNumberer = theParallelNumberer;
    theParallelNumberer->setProcessID(OPS_rank);
    theParallelNumberer->setChannels(numChannels, theChannels);
  }

#  endif

  else {
    opserr << "WARNING No Numberer type exists (Plain, RCM only) \n";
    return TCL_ERROR;
  }
#endif

  return TCL_OK;
}

//
// command invoked to allow the ConstraintHandler object to be built
//
int
specifyConstraintHandler(ClientData clientData, Tcl_Interp *interp, int argc,
                         TCL_Char **argv)
{
  // make sure at least one other argument to contain numberer
  if (argc < 2) {
    opserr << "WARNING need to specify a Nemberer type \n";
    return TCL_ERROR;
  }

  // check argv[1] for type of Numberer and create the object
  if (strcmp(argv[1], "Plain") == 0)
    theHandler = new PlainHandler();

  else if (strcmp(argv[1], "Penalty") == 0) {
    if (argc < 4) {
      opserr << "WARNING: need to specify alpha: handler Penalty alpha \n";
      return TCL_ERROR;
    }
    double alpha1, alpha2;
    if (Tcl_GetDouble(interp, argv[2], &alpha1) != TCL_OK)
      return TCL_ERROR;
    if (Tcl_GetDouble(interp, argv[3], &alpha2) != TCL_OK)
      return TCL_ERROR;
    theHandler = new PenaltyConstraintHandler(alpha1, alpha2);
  }

  /****** adding later
  else if (strcmp(argv[1],"PenaltyNoHomoSPMultipliers") == 0) {
    if (argc < 4) {
      opserr << "WARNING: need to specify alpha: handler Penalty alpha \n";
      return TCL_ERROR;
    }
    double alpha1, alpha2;
    if (Tcl_GetDouble(interp, argv[2], &alpha1) != TCL_OK)
      return TCL_ERROR;
    if (Tcl_GetDouble(interp, argv[3], &alpha2) != TCL_OK)
      return TCL_ERROR;
    theHandler = new PenaltyHandlerNoHomoSPMultipliers(alpha1, alpha2);
  }
  ***********************/
  else if (strcmp(argv[1], "Lagrange") == 0) {
    double alpha1 = 1.0;
    double alpha2 = 1.0;
    if (argc == 4) {
      if (Tcl_GetDouble(interp, argv[2], &alpha1) != TCL_OK)
        return TCL_ERROR;
      if (Tcl_GetDouble(interp, argv[3], &alpha2) != TCL_OK)
        return TCL_ERROR;
    }
    theHandler = new LagrangeConstraintHandler(alpha1, alpha2);
  }

  else if (strcmp(argv[1], "Transformation") == 0) {
    theHandler = new TransformationConstraintHandler();
  }

  else {
    opserr << "WARNING No ConstraintHandler type exists (Plain, Penalty,\n";
    opserr << " Lagrange, Transformation) only\n";
    return TCL_ERROR;
  }
  return TCL_OK;
}



extern int TclAddRecorder(ClientData clientData, Tcl_Interp *interp, int argc,
                          TCL_Char **argv, Domain &theDomain);

int
addRecorder(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  return TclAddRecorder(clientData, interp, argc, argv, *domain);
}

extern int TclAddAlgorithmRecorder(ClientData clientData, Tcl_Interp *interp,
                                   int argc, TCL_Char **argv, Domain &theDomain,
                                   EquiSolnAlgo *theAlgorithm);

int
addAlgoRecorder(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  if (theAlgorithm != 0)
    return TclAddAlgorithmRecorder(clientData, interp, argc, argv, *domain,
                                   theAlgorithm);

  else
    return 0;
}

/*
extern int TclAddDatabase(ClientData clientData, Tcl_Interp *interp, int argc,
                          TCL_Char **argv, Domain &theDomain,
                          FEM_ObjectBroker &theBroker);

int
addDatabase(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  return TclAddDatabase(clientData, interp, argc, argv, theDomain, theBroker);
}

int
groundExcitation(ClientData clientData, Tcl_Interp *interp, int argc,
                  TCL_Char **argv)
{
  G3_Runtime *rt =  G3_getRuntime(interp);
  Domain* the_domain = G3_getDomain(rt);

  // make sure at least one other argument to contain integrator
  if (argc < 2) {
      opserr << "WARNING need to specify the commitTag \n";
      return TCL_ERROR;
  }

  if (strcmp(argv[1],"Single") == 0) {
      if (argc < 4) {
        opserr << "WARNING quake single dof motion\n";
        return TCL_ERROR;
      }

      int dof;
      if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK)
          return TCL_ERROR;

      // read in the ground motion
      GroundMotion *theMotion;
      if (strcmp(argv[3],"ElCentro") == 0) {
          double fact = 1.0;
          if (argc == 5) {
              if (Tcl_GetDouble(interp, argv[4], &fact) != TCL_OK)
                  return TCL_ERROR;
          }
          theMotion = new ElCentroGroundMotion(fact);
      } else {
          opserr << "WARNING quake Single motion - no motion type exists \n";
          return TCL_ERROR;
      }

      Load *theLoad = new SingleExcitation(*theMotion, dof, nextTag++);
      the_domain->addOtherLoad(theLoad);
      return TCL_OK;
  }

  else {
    opserr << "WARNING No quake type exists \n";
    return TCL_ERROR;
  }
}
*/

int
videoPlayer(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 5) {
    opserr << "WARNING want - video -window windowTitle? -file fileName?\n";
    return TCL_ERROR;
  }

  TCL_Char *wTitle = 0;
  TCL_Char *fName = 0;
  TCL_Char *imageName = 0;
  TCL_Char *offsetName = 0;

  int endMarker = 1;
  while (endMarker < (argc - 1)) {
    if (strcmp(argv[endMarker], "-window") == 0) {
      wTitle = argv[endMarker + 1];
      endMarker += 2;
    } else if (strcmp(argv[endMarker], "-file") == 0) {
      fName = argv[endMarker + 1];
      endMarker += 2;
    } else if (strcmp(argv[endMarker], "-image") == 0) {
      imageName = argv[endMarker + 1];
      endMarker += 2;
    } else if (strcmp(argv[endMarker], "-offset") == 0) {
      offsetName = argv[endMarker + 1];
      endMarker += 2;
    } else {
      opserr << "WARNING unknown " << argv[endMarker]
             << " want - video -window windowTitle? -file fileName?\n";

      return TCL_ERROR;
    }
  }

#ifdef _NOGRAPHICS

#else
  if (wTitle != 0 && fName != 0) {
    // delete the old video player if one exists
    if (theTclVideoPlayer != 0)
      delete theTclVideoPlayer;

    // create a new player
    theTclVideoPlayer =
        new TclVideoPlayer(wTitle, fName, imageName, interp, offsetName);
  } else
    return TCL_ERROR;
#endif
  return TCL_OK;
}


int
removeObject(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain * the_domain = G3_getDomain(rt);

  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - remove objectType?\n";
    return TCL_ERROR;
  }

  int tag;
  if ((strcmp(argv[1], "element") == 0) || (strcmp(argv[1], "ele") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove element eleTag?\n";
      return TCL_ERROR;
    }

    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove element tag? failed to read tag: " << argv[2]
             << endln;
      return TCL_ERROR;
    }
    Element *theEle = the_domain->removeElement(tag);
    if (theEle != 0) {
      // we also have to remove any elemental loads from the domain
      LoadPatternIter &theLoadPatterns = the_domain->getLoadPatterns();
      LoadPattern *thePattern;

      // go through all load patterns
      while ((thePattern = theLoadPatterns()) != 0) {
        ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
        ElementalLoad *theLoad;

        // go through all elemental loads in the pattern
        while ((theLoad = theEleLoads()) != 0) {

          // remove & destroy elemental from elemental load if there
          // note - if last element in load, remove the load and delete it

          /* *****************
             int numLoadsLeft = theLoad->removeElement(tag);
             if (numLoadsLeft == 0) {
             thePattern->removeElementalLoad(theLoad->getTag());
             delete theLoad;
             }
          *********************/
        }
      }

      // finally invoke the destructor on the element
      delete theEle;
    }
  }

  else if (strcmp(argv[1], "loadPattern") == 0) {
    if (argc < 3) {
      opserr << "WARNING want - remove loadPattern patternTag?\n";
      return TCL_ERROR;
    }
    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove loadPattern tag? failed to read tag: "
             << argv[2] << endln;
      return TCL_ERROR;
    }
    LoadPattern *thePattern = the_domain->removeLoadPattern(tag);
    if (thePattern != 0) {
      thePattern->clearAll();
      delete thePattern;
    }
  }

  else if ((strcmp(argv[1], "TimeSeries") == 0) ||
           (strcmp(argv[1], "timeSeries") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove loadPattern patternTag?\n";
      return TCL_ERROR;
    }
    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove loadPattern tag? failed to read tag: "
             << argv[2] << endln;
      return TCL_ERROR;
    }
    bool ok = OPS_removeTimeSeries(tag);
    if (ok == true)
      return TCL_OK;
    else
      return TCL_ERROR;
  }

  else if (strcmp(argv[1], "parameter") == 0) {
    if (argc < 3) {
      opserr << "WARNING want - remove parameter paramTag?\n";
      return TCL_ERROR;
    }
    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove parameter tag? failed to read tag: " << argv[2]
             << endln;
      return TCL_ERROR;
    }
    Parameter *theParameter = the_domain->removeParameter(tag);
    if (theParameter != 0) {
      delete theParameter;
    }
  }

  else if (strcmp(argv[1], "node") == 0) {
    if (argc < 3) {
      opserr << "WARNING want - remove node nodeTag?\n";
      return TCL_ERROR;
    }
    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove node tag? failed to read tag: " << argv[2]
             << endln;
      return TCL_ERROR;
    }
    Node *theNode = the_domain->removeNode(tag);
    if (theNode != 0) {
      delete theNode;
    }
    Pressure_Constraint *thePC = the_domain->removePressure_Constraint(tag);
    if (thePC != 0) {
      delete thePC;
    }
  }

  else if (strcmp(argv[1], "recorders") == 0) {
    the_domain->removeRecorders();
  }

  else if ((strcmp(argv[1], "recorder") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove recorder recorderTag?\n";
      return TCL_ERROR;
    }

    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove recorder tag? failed to read tag: " << argv[2]
             << endln;
      return TCL_ERROR;
    }
    return the_domain->removeRecorder(tag);
  }

  else if ((strcmp(argv[1], "timeSeries") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove timeSeries $tag\n";
      return TCL_ERROR;
    }

    if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
      opserr << "WARNING remove timeSeries tag? failed to read tag: " << argv[2]
             << endln;
      return TCL_ERROR;
    }
    return OPS_removeTimeSeries(tag);
  }

  else if ((strcmp(argv[1], "SPconstraint") == 0) ||
           (strcmp(argv[1], "sp") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove SPconstraint spTag? -or- remove "
                "SPconstraint nodeTag? dofTag? <patternTag?>\n";
      return TCL_ERROR;
    }
    if (argc == 3) {
      if (Tcl_GetInt(interp, argv[2], &tag) != TCL_OK) {
        opserr << "WARNING remove sp tag? failed to read tag: " << argv[2]
               << endln;
        return TCL_ERROR;
      }

      SP_Constraint *theSPconstraint = the_domain->removeSP_Constraint(tag);
      if (theSPconstraint != 0) {
        delete theSPconstraint;
      }
    } else {
      int nodeTag, dofTag;
      int patternTag = -1;

      if (Tcl_GetInt(interp, argv[2], &nodeTag) != TCL_OK) {
        opserr << "WARNING remove sp tag? failed to read node tag: " << argv[2]
               << endln;
        return TCL_ERROR;
      }
      if (Tcl_GetInt(interp, argv[3], &dofTag) != TCL_OK) {
        opserr << "WARNING remove sp tag? failed to read dof tag: " << argv[3]
               << endln;
        return TCL_ERROR;
      }

      if (argc == 5) {
        if (Tcl_GetInt(interp, argv[4], &patternTag) != TCL_OK) {
          opserr << "WARNING remove sp tag? failed to read pattern tag: "
                 << argv[4] << endln;
          return TCL_ERROR;
        }
      }
      dofTag--; // one for C++ indexing of dof

      the_domain->removeSP_Constraint(nodeTag, dofTag, patternTag);

      return TCL_OK;
    }
  }

  else if ((strcmp(argv[1], "MPconstraint") == 0) ||
           (strcmp(argv[1], "mp") == 0)) {
    if (argc < 3) {
      opserr << "WARNING want - remove MPconstraint nNodeTag? -or- remove "
                "MPconstraint -tag mpTag\n";
      return TCL_ERROR;
    }
    int nodTag = 0;
    if (argc == 3) {
      if (Tcl_GetInt(interp, argv[2], &nodTag) != TCL_OK) {
        opserr << "WARNING remove mp nodeTag? failed to read nodeTag: "
               << argv[2] << endln;
        return TCL_ERROR;
      }

      the_domain->removeMP_Constraints(nodTag);
      return TCL_OK;
    }
    if (strcmp(argv[2], "-tag") == 0 && argc > 3) {
      if (Tcl_GetInt(interp, argv[3], &nodTag) != TCL_OK) {
        opserr << "WARNING remove mp -tag mpTag? failed to read mpTag: "
               << argv[3] << endln;
        return TCL_ERROR;
      }

      the_domain->removeMP_Constraint(nodTag);
      return TCL_OK;
    }
  }

#ifdef _RELIABILITY
  // AddingSensitivity:BEGIN ///////////////////////////////////////
  else if (strcmp(argv[1], "randomVariable") == 0) {
    int rvTag;
    if (Tcl_GetInt(interp, argv[2], &rvTag) != TCL_OK) {
      opserr << "WARNING invalid input: rvTag \n";
      return TCL_ERROR;
    }
    ReliabilityDomain *theReliabilityDomain =
        theReliabilityBuilder->getReliabilityDomain();
    theReliabilityDomain->removeRandomVariable(rvTag);
  } else if (strcmp(argv[1], "performanceFunction") == 0) {
    int lsfTag;
    if (Tcl_GetInt(interp, argv[2], &lsfTag) != TCL_OK) {
      opserr << "WARNING invalid input: lsfTag \n";
      return TCL_ERROR;
    }
    ReliabilityDomain *theReliabilityDomain =
        theReliabilityBuilder->getReliabilityDomain();
    theReliabilityDomain->removeLimitStateFunction(lsfTag);
  } else if (strcmp(argv[1], "cutset") == 0) {
    int cutTag;
    if (Tcl_GetInt(interp, argv[2], &cutTag) != TCL_OK) {
      opserr << "WARNING invalid input: cutTag \n";
      return TCL_ERROR;
    }
    ReliabilityDomain *theReliabilityDomain =
        theReliabilityBuilder->getReliabilityDomain();
    theReliabilityDomain->removeCutset(cutTag);
  } else if (strcmp(argv[1], "sensitivityAlgorithm") == 0) {
    if (theSensitivityAlgorithm != 0) {
      // the_static_analysis->setSensitivityAlgorithm(0);
      theSensitivityAlgorithm = 0;
      theSensitivityIntegrator = 0;
    }
  }
// AddingSensitivity:END ///////////////////////////////////////
#endif

  else
    opserr << "WARNING remove " << argv[1] << " not supported" << endln;

  return TCL_OK;
}

int
nodeDisp(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - nodeDisp nodeTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeDisp nodeTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING nodeDisp nodeTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;

  const Vector *nodalResponse = domain->getNodeResponse(tag, Disp);

  if (nodalResponse == 0)
    return TCL_ERROR;

  int size = nodalResponse->Size();

  if (dof >= 0) {

    if (dof >= size) {
      opserr << "WARNING nodeDisp nodeTag? dof? - dofTag? too large\n";
      return TCL_ERROR;
    }

    double value = (*nodalResponse)(dof);

    // now we copy the value to the tcl string that is returned

    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    //  sprintf(interp->result,"%35.20f ",value);
  } else {
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", (*nodalResponse)(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
nodeReaction(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - nodeReaction nodeTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeReaction nodeTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING nodeReaction nodeTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;

  const Vector *nodalResponse = domain->getNodeResponse(tag, Reaction);

  if (nodalResponse == 0)
    return TCL_ERROR;

  int size = nodalResponse->Size();

  if (dof >= 0) {

    if (dof >= size) {
      opserr << "WARNING nodeReaction nodeTag? dof? - dofTag? too large\n";
      return TCL_ERROR;
    }

    double value = (*nodalResponse)(dof);

    // now we copy the value to the tcl string that is returned

    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    //      sprintf(interp->result,"%35.20f ",value);
  } else {
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", (*nodalResponse)(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
nodeUnbalance(ClientData clientData, Tcl_Interp *interp, int argc,
              TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - nodeUnbalance nodeTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr
        << "WARNING nodeUnbalance nodeTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING nodeUnbalance nodeTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;

  const Vector *nodalResponse = domain->getNodeResponse(tag, Unbalance);

  if (nodalResponse == 0)
    return TCL_ERROR;

  int size = nodalResponse->Size();

  if (dof >= 0) {

    if (dof >= size) {
      opserr << "WARNING nodeUnbalance nodeTag? dof? - dofTag? too large\n";
      return TCL_ERROR;
    }

    double value = (*nodalResponse)(dof);

    // now we copy the value to the tcl string that is returned
    //      sprintf(interp->result,"%35.20f ",value);

    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
  } else {
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", (*nodalResponse)(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
nodeEigenvector(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - nodeEigenVector nodeTag? eigenVector? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int eigenvector = 0;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr
        << "WARNING nodeEigenvector nodeTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (Tcl_GetInt(interp, argv[2], &eigenvector) != TCL_OK) {
    opserr << "WARNING nodeEigenvector nodeTag? dof? - could not read dof? \n";
    return TCL_ERROR;
  }

  if (argc > 3) {
    if (Tcl_GetInt(interp, argv[3], &dof) != TCL_OK) {
      opserr
          << "WARNING nodeEigenvector nodeTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;
  eigenvector--;
  Node *theNode = domain->getNode(tag);
  const Matrix &theEigenvectors = theNode->getEigenvectors();

  int size = theEigenvectors.noRows();
  int numEigen = theEigenvectors.noCols();

  if (eigenvector < 0 || eigenvector >= numEigen) {
    opserr << "WARNING nodeEigenvector nodeTag? dof? - eigenvecor too large\n";
    return TCL_ERROR;
  }

  if (dof >= 0) {
    if (dof >= size) {
      opserr << "WARNING nodeEigenvector nodeTag? dof? - dofTag? too large\n";
      return TCL_ERROR;
    }

    double value = theEigenvectors(dof, eigenvector);
    // now we copy the value to the tcl string that is returned
    //      sprintf(interp->result,"%35.20f ",value);
    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
  } else {

    char buffer[40];
    for (int i = 0; i < size; i++) {
      double value = theEigenvectors(i, eigenvector);
      sprintf(buffer, "%35.20f", value);
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
eleForce(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - eleForce eleTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleForce eleTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING eleForce eleTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;

  /*
  Element *theEle = the_domain->getElement(tag);
  if (theEle == 0)
    return TCL_ERROR;

  const Vector &force = theEle->getResistingForce();
  */

  const char *myArgv[1];
  char myArgv0[8];
  strcpy(myArgv0, "forces");
  myArgv[0] = myArgv0;

  const Vector *force = domain->getElementResponse(tag, &myArgv[0], 1);
  if (force != 0) {
    int size = force->Size();

    if (dof >= 0) {

      if (size < dof)
        return TCL_ERROR;

      double value = (*force)(dof);

      // now we copy the value to the tcl string that is returned
      //	sprintf(interp->result,"%35.20f",value);

      char buffer[40];
      sprintf(buffer, "%35.20f", value);
      Tcl_SetResult(interp, buffer, TCL_VOLATILE);

    } else {
      char buffer[40];
      for (int i = 0; i < size; i++) {
        sprintf(buffer, "%35.20f", (*force)(i));
        Tcl_AppendResult(interp, buffer, NULL);
      }
    }
  } else {
    opserr << "WARNING - failed to retrieve element force.\n";
    return TCL_ERROR;
  }
  return TCL_OK;
}

int
localForce(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - localForce eleTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING localForce eleTag? dof? - could not read eleTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING localForce eleTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;


  const char *myArgv[1];
  char myArgv0[80];
  strcpy(myArgv0, "localForces");
  myArgv[0] = myArgv0;

  const Vector *force = theDomain.getElementResponse(tag, &myArgv[0], 1);
  if (force != 0) {
    int size = force->Size();

    if (dof >= 0) {

      if (size < dof)
        return TCL_ERROR;

      double value = (*force)(dof);

      // now we copy the value to the tcl string that is returned
      //	sprintf(interp->result,"%35.20f",value);

      char buffer[40];
      sprintf(buffer, "%35.20f", value);
      Tcl_SetResult(interp, buffer, TCL_VOLATILE);

    } else {
      char buffer[40];
      for (int i = 0; i < size; i++) {
        sprintf(buffer, "%35.20f", (*force)(i));
        Tcl_AppendResult(interp, buffer, NULL);
      }
    }
  }

  return TCL_OK;
}

int
eleDynamicalForce(ClientData clientData, Tcl_Interp *interp, int argc,
                  TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - eleForce eleTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleForce eleTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING eleForce eleTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;
  Element *theEle = theDomain.getElement(tag);
  if (theEle == 0)
    return TCL_ERROR;

  const Vector &force = theEle->getResistingForceIncInertia();
  int size = force.Size();

  if (dof >= 0) {

    if (size < dof)
      return TCL_ERROR;

    double value = force(dof);

    // now we copy the value to the tcl string that is returned
    //      sprintf(interp->result,"%35.20f",value);
    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  } else {
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", force(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
eleResponse(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain* the_domain = G3_getDomain(rt);
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - eleResponse eleTag? eleArgs...\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleForce eleTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  /*
  Element *theEle = the_domain->getElement(tag);
  if (theEle == 0)
    return TCL_ERROR;

  DummyStream dummy;
  Response *theResponse = theEle->setResponse(argv+2, argc-2, dummy);
  if (theResponse == 0) {
    return TCL_ERROR;
  }

  if (theResponse->getResponse() < 0) {
    delete theResponse;
    return TCL_ERROR;
  }

  Information &eleInfo = theResponse->getInformation();
  const Vector &data = eleInfo.getData();
  */

  const Vector *data = the_domain->getElementResponse(tag, argv + 2, argc - 2);
  if (data != 0) {
    int size = data->Size();
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%f ", (*data)(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }
  return TCL_OK;
}

int
findID(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - findNodesWithID ?id\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleForce eleTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  NodeIter &theNodes = theDomain.getNodes();
  Node *theNode;
  char buffer[20] = {0};

  while ((theNode = theNodes()) != 0) {
    DOF_Group *theGroup = theNode->getDOF_GroupPtr();
    if (theGroup != 0) {
      const ID &nodeID = theGroup->getID();
      for (int i = 0; i < nodeID.Size(); i++) {
        if (nodeID(i) == tag) {
          sprintf(buffer, "%d ", theNode->getTag());
          Tcl_AppendResult(interp, buffer, NULL);
          break;
        }
      }
    }
  }

  return TCL_OK;
}

int
nodeCoord(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - nodeCoord nodeTag? <dim?>\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeCoord nodeTag? dim? - could not read nodeTag? \n";
    return TCL_ERROR;
  }

  int dim = -1;

  if (argc > 2) {
    if (strcmp(argv[2], "X") == 0 || strcmp(argv[2], "x") == 0 ||
        strcmp(argv[2], "1") == 0)
      dim = 0;
    else if (strcmp(argv[2], "Y") == 0 || strcmp(argv[2], "y") == 0 ||
             strcmp(argv[2], "2") == 0)
      dim = 1;
    else if (strcmp(argv[2], "Z") == 0 || strcmp(argv[2], "z") == 0 ||
             strcmp(argv[2], "3") == 0)
      dim = 2;
    else {
      opserr << "WARNING nodeCoord nodeTag? dim? - could not read dim? \n";
      return TCL_ERROR;
    }
  }

  Node *theNode = theDomain.getNode(tag);

  if (theNode == 0) {
    return TCL_ERROR;
  }

  const Vector &coords = theNode->getCrds();

  int size = coords.Size();
  if (dim == -1) {
    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", coords(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
    return TCL_OK;
  } else if (dim < size) {
    double value = coords(dim); // -1 for OpenSees vs C indexing
    //    sprintf(interp->result,"%35.20f",value);
    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);

    return TCL_OK;
  }

  return TCL_ERROR;
}

int
fixedNodes(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  SP_Constraint *theSP;
  SP_ConstraintIter &spIter = theDomain.getDomainAndLoadPatternSPs();

  // get unique constrained nodes with set
  set<int> tags;
  int tag;
  while ((theSP = spIter()) != 0) {
    tag = theSP->getNodeTag();
    tags.insert(tag);
  }
  // assign set to vector and sort
  vector<int> tagv;
  tagv.assign(tags.begin(), tags.end());
  sort(tagv.begin(), tagv.end());
  // loop through unique, sorted tags, adding to output
  char buffer[20];
  for (int tag : tagv) {
    sprintf(buffer, "%d ", tag);
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
fixedDOFs(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  if (argc < 2) {
    opserr << "WARNING want - fixedDOFs fNode?\n";
    return TCL_ERROR;
  }

  int fNode;
  if (Tcl_GetInt(interp, argv[1], &fNode) != TCL_OK) {
    opserr << "WARNING fixedDOFs fNode? - could not read fNode? \n";
    return TCL_ERROR;
  }

  SP_Constraint *theSP;
  SP_ConstraintIter &spIter = theDomain.getDomainAndLoadPatternSPs();

  int tag;
  Vector fixed(6);
  while ((theSP = spIter()) != 0) {
    tag = theSP->getNodeTag();
    if (tag == fNode) {
      fixed(theSP->getDOF_Number()) = 1;
    }
  }

  char buffer[20];
  for (int i = 0; i < 6; i++) {
    if (fixed(i) == 1) {
      sprintf(buffer, "%d ", i + 1);
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
constrainedNodes(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv)
{
  bool all = 1;
  int rNode;
  if (argc > 1) {
    if (Tcl_GetInt(interp, argv[1], &rNode) != TCL_OK) {
      opserr << "WARNING constrainedNodes <rNode?> - could not read rNode? \n";
      return TCL_ERROR;
    }
    all = 0;
  }

  MP_Constraint *theMP;
  MP_ConstraintIter &mpIter = theDomain.getMPs();

  // get unique constrained nodes with set
  set<int> tags;
  int tag;
  while ((theMP = mpIter()) != 0) {
    tag = theMP->getNodeConstrained();
    if (all || rNode == theMP->getNodeRetained()) {
      tags.insert(tag);
    }
  }
  // assign set to vector and sort
  vector<int> tagv;
  tagv.assign(tags.begin(), tags.end());
  sort(tagv.begin(), tagv.end());
  // loop through unique, sorted tags, adding to output
  char buffer[20];
  for (int tag : tagv) {
    sprintf(buffer, "%d ", tag);
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
constrainedDOFs(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  if (argc < 2) {
    opserr << "WARNING want - constrainedDOFs cNode? <rNode?> <rDOF?>\n";
    return TCL_ERROR;
  }

  int cNode;
  if (Tcl_GetInt(interp, argv[1], &cNode) != TCL_OK) {
    opserr << "WARNING constrainedDOFs cNode? <rNode?> <rDOF?> - could not "
              "read cNode? \n";
    return TCL_ERROR;
  }

  int rNode;
  bool allNodes = 1;
  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &rNode) != TCL_OK) {
      opserr << "WARNING constrainedDOFs cNode? <rNode?> <rDOF?> - could not "
                "read rNode? \n";
      return TCL_ERROR;
    }
    allNodes = 0;
  }

  int rDOF;
  bool allDOFs = 1;
  if (argc > 3) {
    if (Tcl_GetInt(interp, argv[3], &rDOF) != TCL_OK) {
      opserr << "WARNING constrainedDOFs cNode? <rNode?> <rDOF?> - could not "
                "read rDOF? \n";
      return TCL_ERROR;
    }
    rDOF--;
    allDOFs = 0;
  }

  MP_Constraint *theMP;
  MP_ConstraintIter &mpIter = theDomain.getMPs();

  int tag;
  int i;
  int n;
  Vector constrained(6);
  while ((theMP = mpIter()) != 0) {
    tag = theMP->getNodeConstrained();
    if (tag == cNode) {
      if (allNodes || rNode == theMP->getNodeRetained()) {
        const ID &cDOFs = theMP->getConstrainedDOFs();
        n = cDOFs.Size();
        if (allDOFs) {
          for (i = 0; i < n; i++) {
            constrained(cDOFs(i)) = 1;
          }
        } else {
          const ID &rDOFs = theMP->getRetainedDOFs();
          for (i = 0; i < n; i++) {
            if (rDOF == rDOFs(i))
              constrained(cDOFs(i)) = 1;
          }
        }
      }
    }
  }
  char buffer[20];
  for (int i = 0; i < 6; i++) {
    if (constrained(i) == 1) {
      sprintf(buffer, "%d ", i + 1);
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
retainedNodes(ClientData clientData, Tcl_Interp *interp, int argc,
              TCL_Char **argv)
{
  bool all = 1;
  int cNode;
  if (argc > 1) {
    if (Tcl_GetInt(interp, argv[1], &cNode) != TCL_OK) {
      opserr << "WARNING retainedNodes <cNode?> - could not read cNode? \n";
      return TCL_ERROR;
    }
    all = 0;
  }

  MP_Constraint *theMP;
  MP_ConstraintIter &mpIter = theDomain.getMPs();

  // get unique constrained nodes with set
  set<int> tags;
  int tag;
  while ((theMP = mpIter()) != 0) {
    tag = theMP->getNodeRetained();
    if (all || cNode == theMP->getNodeConstrained()) {
      tags.insert(tag);
    }
  }
  // assign set to vector and sort
  vector<int> tagv;
  tagv.assign(tags.begin(), tags.end());
  sort(tagv.begin(), tagv.end());
  // loop through unique, sorted tags, adding to output
  char buffer[20];
  for (int tag : tagv) {
    sprintf(buffer, "%d ", tag);
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
retainedDOFs(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{

  if (argc < 2) {
    opserr << "WARNING want - retainedDOFs rNode? <cNode?> <cDOF?>\n";
    return TCL_ERROR;
  }

  int rNode;
  if (Tcl_GetInt(interp, argv[1], &rNode) != TCL_OK) {
    opserr << "WARNING retainedDOFs rNode? <cNode?> <cDOF?> - could not read "
              "rNode? \n";
    return TCL_ERROR;
  }

  int cNode;
  bool allNodes = 1;
  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &cNode) != TCL_OK) {
      opserr << "WARNING retainedDOFs rNode? <cNode?> <cDOF?> - could not read "
                "cNode? \n";
      return TCL_ERROR;
    }
    allNodes = 0;
  }

  int cDOF;
  bool allDOFs = 1;
  if (argc > 3) {
    if (Tcl_GetInt(interp, argv[3], &cDOF) != TCL_OK) {
      opserr << "WARNING retainedDOFs rNode? <cNode?> <cDOF?> - could not read "
                "cDOF? \n";
      return TCL_ERROR;
    }
    cDOF--;
    allDOFs = 0;
  }

  MP_Constraint *theMP;
  MP_ConstraintIter &mpIter = theDomain.getMPs();

  int tag;
  int i;
  int n;
  Vector retained(6);
  while ((theMP = mpIter()) != 0) {
    tag = theMP->getNodeRetained();
    if (tag == rNode) {
      if (allNodes || cNode == theMP->getNodeConstrained()) {
        const ID &rDOFs = theMP->getRetainedDOFs();
        n = rDOFs.Size();
        if (allDOFs) {
          for (i = 0; i < n; i++) {
            retained(rDOFs(i)) = 1;
          }
        } else {
          const ID &cDOFs = theMP->getConstrainedDOFs();
          for (i = 0; i < n; i++) {
            if (cDOF == cDOFs(i))
              retained(rDOFs(i)) = 1;
          }
        }
      }
    }
  }
  char buffer[20];
  for (int i = 0; i < 6; i++) {
    if (retained(i) == 1) {
      sprintf(buffer, "%d ", i + 1);
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
setNodeCoord(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 4) {
    opserr << "WARNING want - setNodeCoord nodeTag? dim? value?\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING setNodeCoord nodeTag? dim? value? - could not read "
              "nodeTag? \n";
    return TCL_ERROR;
  }

  int dim;
  double value;

  if (Tcl_GetInt(interp, argv[2], &dim) != TCL_OK) {
    opserr
        << "WARNING setNodeCoord nodeTag? dim? value? - could not read dim? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &value) != TCL_OK) {
    opserr << "WARNING setNodeCoord nodeTag? dim? value? - could not read "
              "value? \n";
    return TCL_ERROR;
  }

  Node *theNode = theDomain.getNode(tag);

  if (theNode == 0) {
    return TCL_ERROR;
  }

  Vector coords(theNode->getCrds());
  coords(dim - 1) = value;
  theNode->setCrds(coords);

  return TCL_OK;
}

int
updateElementDomain(ClientData clientData, Tcl_Interp *interp, int argc,
                    TCL_Char **argv)
{
  // Need to "setDomain" to make the change take effect.
  G3_Runtime* rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  ElementIter &theElements = the_domain->getElements();
  Element *theElement;
  while ((theElement = theElements()) != 0) {
    theElement->setDomain(the_domain);
  }
  return 0;
}

int
getNDM(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int ndm;
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc > 1) {
    int tag;
    if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
      opserr << "WARNING ndm nodeTag? \n";
      return TCL_ERROR;
    }
    Node *theNode = the_domain->getNode(tag);
    if (theNode == 0) {
      opserr << "WARNING nodeTag " << tag << " does not exist \n";
      return TCL_ERROR;
    }
    const Vector &coords = theNode->getCrds();
    ndm = coords.Size();
  } else {
    if (G3_getModelBuilder(rt) == 0) {
      return TCL_OK;
    } else {
      ndm = G3_getNDM(rt);
    }
  }

  char buffer[20];
  sprintf(buffer, "%d", ndm);
  Tcl_AppendResult(interp, buffer, NULL);

  return TCL_OK;
}

int
getNDF(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int ndf;
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc > 1) {
    int tag;
    if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
      opserr << "WARNING ndf nodeTag? \n";
      return TCL_ERROR;
    }
    Node *theNode = the_domain->getNode(tag);
    if (theNode == 0) {
      opserr << "WARNING nodeTag " << tag << " does not exist \n";
      return TCL_ERROR;
    }
    ndf = theNode->getNumberDOF();
  } else {
    if (theBuilder == 0) {
      return TCL_OK;
    } else {
      ndf = G3_getNDF(rt);
    }
  }

  char buffer[G3_NUM_DOF_BUFFER];
  if (abs(ndf) <  G3_MAX_NUM_DOFS){
    sprintf(buffer, "%d", ndf);
  } else {
    opserr << "ERROR -- Invalid DOF count encountered; got '" << ndf << "'.\n";
    return TCL_ERROR;
  }

  Tcl_AppendResult(interp, buffer, NULL);

  return TCL_OK;
}

int
eleType(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc < 2) {
    opserr << "WARNING want - eleType eleTag?\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleType eleTag? \n";
    return TCL_ERROR;
  }

  char buffer[80];
  Element *theElement = the_domain->getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING eleType ele " << tag << " not found" << endln;
    return TCL_ERROR;
  }
  const char *type = theElement->getClassType();
  sprintf(buffer, "%s", type);
  Tcl_AppendResult(interp, buffer, NULL);

  return TCL_OK;
}

int
eleNodes(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc < 2) {
    opserr << "WARNING want - eleNodes eleTag?\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING eleNodes eleTag? \n";
    return TCL_ERROR;
  }

  char buffer[20];

  const char *myArgv[1];
  char myArgv0[80];
  strcpy(myArgv0, "nodeTags");
  myArgv[0] = myArgv0;

  // const Vector *tags = the_domain->getElementResponse(tag, &myArgv[0], 1);
  Element *theElement = the_domain->getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING eleNodes ele " << tag << " not found" << endln;
    return TCL_ERROR;
  }
  int numTags = theElement->getNumExternalNodes();
  const ID &tags = theElement->getExternalNodes();
  for (int i = 0; i < numTags; i++) {
    sprintf(buffer, "%d ", tags(i));
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
nodeDOFs(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc < 2) {
    opserr << "WARNING want - nodeDOFs nodeTag?\n";
    return TCL_ERROR;
  }

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeMass nodeTag? nodeDOF? \n";
    return TCL_ERROR;
  }

  char buffer[40];

  Node *theNode = the_domain->getNode(tag);
  if (theNode == 0) {
    opserr << "WARNING nodeDOFs node " << tag << " not found" << endln;
    return TCL_ERROR;
  }
  int numDOF = theNode->getNumberDOF();

  DOF_Group *theDOFgroup = theNode->getDOF_GroupPtr();
  if (theDOFgroup == 0) {
    opserr << "WARNING nodeDOFs DOF group null" << endln;
    return -1;
  }
  const ID &eqnNumbers = theDOFgroup->getID();
  for (int i = 0; i < numDOF; i++) {
    sprintf(buffer, "%d ", eqnNumbers(i));
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
nodeMass(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);

  if (argc < 3) {
    opserr << "WARNING want - nodeMass nodeTag? nodeDOF?\n";
    return TCL_ERROR;
  }

  int tag, dof;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeMass nodeTag? nodeDOF? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
    opserr << "WARNING nodeMass nodeTag? nodeDOF? \n";
    return TCL_ERROR;
  }

  char buffer[40];

  Node *theNode = the_domain->getNode(tag);
  if (theNode == 0) {
    opserr << "WARNING nodeMass node " << tag << " not found" << endln;
    return TCL_ERROR;
  }
  int numDOF = theNode->getNumberDOF();
  if (dof < 1 || dof > numDOF) {
    opserr << "WARNING nodeMass dof " << dof << " not in range" << endln;
    return TCL_ERROR;
  } else {
    const Matrix &mass = theNode->getMass();
    sprintf(buffer, "%35.20f", mass(dof - 1, dof - 1));
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
nodePressure(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  G3_Runtime *rt = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);
  if (argc < 2) {
    opserr << "WARNING: want - nodePressure nodeTag?\n";
    return TCL_ERROR;
  }
  int tag;
  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING: nodePressure " << argv[1] << "\n";
    return TCL_ERROR;
  }
  double pressure = 0.0;
  Pressure_Constraint *thePC = theDomain.getPressure_Constraint(tag);
  if (thePC != 0) {
    pressure = thePC->getPressure();
  }
  char buffer[80];
  sprintf(buffer, "%35.20f", pressure);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
nodeBounds(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int requiredDataSize = 20 * 6;
  if (requiredDataSize > resDataSize) {
    if (resDataPtr != 0) {
      delete[] resDataPtr;
    }
    resDataPtr = new char[requiredDataSize];
    resDataSize = requiredDataSize;
  }

  for (int i = 0; i < requiredDataSize; i++)
    resDataPtr[i] = '\n';

  const Vector &bounds = theDomain.getPhysicalBounds();

  int cnt = 0;
  for (int j = 0; j < 6; j++) {
    cnt += sprintf(&resDataPtr[cnt], "%.6e  ", bounds(j));
  }

  Tcl_SetResult(interp, resDataPtr, TCL_STATIC);

  return TCL_OK;
}

int
nodeVel(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - nodeVel nodeTag? <dof?>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING nodeVel nodeTag? dof? - could not read nodeTag? \n";
    return TCL_ERROR;
  }
  if (argc > 2) {
    if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
      opserr << "WARNING nodeVel nodeTag? dof? - could not read dof? \n";
      return TCL_ERROR;
    }
  }

  dof--;

  const Vector *nodalResponse = theDomain.getNodeResponse(tag, Vel);

  if (nodalResponse == 0)
    return TCL_ERROR;

  int size = nodalResponse->Size();

  if (dof >= 0) {
    if (size < dof)
      return TCL_ERROR;

    double value = (*nodalResponse)(dof);

    // now we copy the value to the tcl string that is returned
    //      sprintf(interp->result,"%35.20f",value);
    char buffer[40];
    sprintf(buffer, "%35.20f", value);
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  } else {

    char buffer[40];
    for (int i = 0; i < size; i++) {
      sprintf(buffer, "%35.20f", (*nodalResponse)(i));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  return TCL_OK;
}

int
setNodeVel(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 4) {
    opserr << "WARNING want - setNodeVel nodeTag? dof? value? <-commit>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;
  double value = 0.0;
  bool commit = false;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING setNodeVel nodeTag? dof? value?- could not read "
              "nodeTag? \n";
    return TCL_ERROR;
  }

  Node *theNode = theDomain.getNode(tag);
  if (theNode == 0) {
    opserr << "WARNING setNodeVel -- node with tag " << tag << " not found"
           << endln;
    return TCL_ERROR;
  }

  if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
    opserr << "WARNING setNodeVel nodeTag? dof? value?- could not read dof? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &value) != TCL_OK) {
    opserr
        << "WARNING setNodeVel nodeTag? dof? value?- could not read value? \n";
    return TCL_ERROR;
  }
  if (argc > 4 && strcmp(argv[4], "-commit") == 0)
    commit = true;

  dof--;

  int numDOF = theNode->getNumberDOF();

  if (dof >= 0 && dof < numDOF) {
    Vector vel(numDOF);
    vel = theNode->getVel();
    vel(dof) = value;
    theNode->setTrialVel(vel);
  }
  if (commit)
    theNode->commitState();

  return TCL_OK;
}

int
setNodeDisp(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 4) {
    opserr << "WARNING want - setNodeDisp nodeTag? dof? value? <-commit>\n";
    return TCL_ERROR;
  }

  int tag;
  int dof = -1;
  double value = 0.0;
  bool commit = false;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING setNodeDisp nodeTag? dof? value?- could not read "
              "nodeTag? \n";
    return TCL_ERROR;
  }

  Node *theNode = theDomain.getNode(tag);
  if (theNode == 0) {
    opserr << "WARNING setNodeDisp -- node with tag " << tag << " not found"
           << endln;
    return TCL_ERROR;
  }

  if (Tcl_GetInt(interp, argv[2], &dof) != TCL_OK) {
    opserr
        << "WARNING setNodeDisp nodeTag? dof? value?- could not read dof? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &value) != TCL_OK) {
    opserr
        << "WARNING setNodeDisp nodeTag? dof? value?- could not read value? \n";
    return TCL_ERROR;
  }
  if (argc > 4 && strcmp(argv[4], "-commit") == 0)
    commit = true;

  dof--;

  int numDOF = theNode->getNumberDOF();

  if (dof >= 0 && dof < numDOF) {
    Vector vel(numDOF);
    vel = theNode->getDisp();
    vel(dof) = value;
    theNode->setTrialDisp(vel);
  }
  if (commit)
    theNode->commitState();

  return TCL_OK;
}




int
sectionForce(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - sectionForce eleTag? <secNum?> dof? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionForce: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, dof;
  int secNum = 0;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING sectionForce eleTag? secNum? dof? - could not read "
              "eleTag? \n";
    return TCL_ERROR;
  }

  // Make this work for zeroLengthSection too
  int currentArg = 2;
  if (argc > 3) {
    if (Tcl_GetInt(interp, argv[currentArg++], &secNum) != TCL_OK) {
      opserr << "WARNING sectionForce eleTag? secNum? dof? - could not read "
                "secNum? \n";
      return TCL_ERROR;
    }
  }
  if (Tcl_GetInt(interp, argv[currentArg++], &dof) != TCL_OK) {
    opserr
        << "WARNING sectionForce eleTag? secNum? dof? - could not read dof? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionForce element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 3;
  char a[80] = "section";
  char b[80];
  sprintf(b, "%d", secNum);
  char c[80] = "force";
  const char *argvv[3];
  argvv[0] = a;
  argvv[1] = b;
  argvv[2] = c;
  if (argc < 4) { // For zeroLengthSection
    argcc = 2;
    argvv[1] = c;
  }

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);

  char buffer[40];
  sprintf(buffer, "%12.8g", theVec(dof - 1));

  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  delete theResponse;

  return TCL_OK;
}

int
sectionDeformation(ClientData clientData, Tcl_Interp *interp, int argc,
                   TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 4) {
    opserr << "WARNING want - sectionDeformation eleTag? secNum? dof? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, secNum, dof;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING sectionDeformation eleTag? secNum? dof? - could not "
              "read eleTag? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING sectionDeformation eleTag? secNum? dof? - could not "
              "read secNum? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[3], &dof) != TCL_OK) {
    opserr << "WARNING sectionDeformation eleTag? secNum? dof? - could not "
              "read dof? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionDeformation element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 3;
  char a[80] = "section";
  char b[80];
  sprintf(b, "%d", secNum);
  char c[80] = "deformation";
  const char *argvv[3];
  argvv[0] = a;
  argvv[1] = b;
  argvv[2] = c;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);

  char buffer[40];
  sprintf(buffer, "%12.8g", theVec(dof - 1));

  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  delete theResponse;

  return TCL_OK;
}

int
sectionLocation(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - sectionLocation eleTag? secNum? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, secNum;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING sectionLocation eleTag? secNum? - could not read "
              "eleTag? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING sectionLocation eleTag? secNum? - could not read "
              "secNum? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionLocation element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 1;
  char a[80] = "integrationPoints";
  const char *argvv[1];
  argvv[0] = a;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);

  char buffer[40];
  sprintf(buffer, "%12.8g", theVec(secNum - 1));

  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  delete theResponse;

  return TCL_OK;
}

int
sectionWeight(ClientData clientData, Tcl_Interp *interp, int argc,
              TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - sectionWeight eleTag? secNum? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, secNum;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr
        << "WARNING sectionWeight eleTag? secNum? - could not read eleTag? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr
        << "WARNING sectionWeight eleTag? secNum? - could not read secNum? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionWeight element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 1;
  char a[80] = "integrationWeights";
  const char *argvv[1];
  argvv[0] = a;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);

  char buffer[40];
  sprintf(buffer, "%12.8g", theVec(secNum - 1));

  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  delete theResponse;

  return TCL_OK;
}

int
sectionStiffness(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - sectionStiffness eleTag? secNum? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, secNum;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING sectionStiffness eleTag? secNum? - could not read "
              "eleTag? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING sectionStiffness eleTag? secNum? - could not read "
              "secNum? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionStiffness element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 3;
  char a[80] = "section";
  char b[80];
  sprintf(b, "%d", secNum);
  char c[80] = "stiffness";
  const char *argvv[3];
  argvv[0] = a;
  argvv[1] = b;
  argvv[2] = c;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Matrix &theMat = *(info.theMatrix);
  int nsdof = theMat.noCols();

  char buffer[200];
  for (int i = 0; i < nsdof; i++) {
    for (int j = 0; j < nsdof; j++) {
      sprintf(buffer, "%12.8g ", theMat(i, j));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  delete theResponse;

  return TCL_OK;
}

int
sectionFlexibility(ClientData clientData, Tcl_Interp *interp, int argc,
                   TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 3) {
    opserr << "WARNING want - sectionFlexibility eleTag? secNum? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag, secNum;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING sectionFlexibility eleTag? secNum? - could not read "
              "eleTag? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING sectionFlexibility eleTag? secNum? - could not read "
              "secNum? \n";
    return TCL_ERROR;
  }

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING sectionFlexibility element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 3;
  char a[80] = "section";
  char b[80];
  sprintf(b, "%d", secNum);
  char c[80] = "flexibility";
  const char *argvv[3];
  argvv[0] = a;
  argvv[1] = b;
  argvv[2] = c;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Matrix &theMat = *(info.theMatrix);
  int nsdof = theMat.noCols();

  char buffer[200];
  for (int i = 0; i < nsdof; i++) {
    for (int j = 0; j < nsdof; j++) {
      sprintf(buffer, "%12.8g ", theMat(i, j));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  delete theResponse;

  return TCL_OK;
}

int
basicDeformation(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - basicDeformation eleTag? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING basicDeformation eleTag? dofNum? - could not read "
              "eleTag? \n";
    return TCL_ERROR;
  }
  /*
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING basicDeformation eleTag? dofNum? - could not read dofNum?
  \n"; return TCL_ERROR;
  }
  */

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING basicDeformation element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 1;
  char a[80] = "basicDeformation";
  const char *argvv[1];
  argvv[0] = a;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);
  int nbf = theVec.Size();

  char buffer[200];
  for (int i = 0; i < nbf; i++) {
    sprintf(buffer, "%12.8f ", theVec(i));
    Tcl_AppendResult(interp, buffer, NULL);
  }

  delete theResponse;

  return TCL_OK;
}

int
basicForce(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - basicForce eleTag? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING basicForce eleTag? dofNum? - could not read eleTag? \n";
    return TCL_ERROR;
  }
  /*
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING basicDeformation eleTag? dofNum? - could not read dofNum?
  \n"; return TCL_ERROR;
  }
  */

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING basicDeformation element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 1;
  char a[80] = "basicForce";
  const char *argvv[1];
  argvv[0] = a;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Vector &theVec = *(info.theVector);
  int nbf = theVec.Size();

  char buffer[200];
  for (int i = 0; i < nbf; i++) {
    sprintf(buffer, "%12.8f ", theVec(i));
    Tcl_AppendResult(interp, buffer, NULL);
  }

  delete theResponse;

  return TCL_OK;
}

int
basicStiffness(ClientData clientData, Tcl_Interp *interp, int argc,
               TCL_Char **argv)
{
  // make sure at least one other argument to contain type of system
  if (argc < 2) {
    opserr << "WARNING want - basicStiffness eleTag? \n";
    return TCL_ERROR;
  }

  // opserr << "sectionDeformation: ";
  // for (int i = 0; i < argc; i++)
  //  opserr << argv[i] << ' ' ;
  // opserr << endln;

  int tag;

  if (Tcl_GetInt(interp, argv[1], &tag) != TCL_OK) {
    opserr << "WARNING basicStiffness eleTag? - could not read eleTag? \n";
    return TCL_ERROR;
  }
  /*
  if (Tcl_GetInt(interp, argv[2], &secNum) != TCL_OK) {
    opserr << "WARNING basicDeformation eleTag? dofNum? - could not read dofNum?
  \n"; return TCL_ERROR;
  }
  */

  Element *theElement = theDomain.getElement(tag);
  if (theElement == 0) {
    opserr << "WARNING basicStiffness element with tag " << tag
           << " not found in domain \n";
    return TCL_ERROR;
  }

  int argcc = 1;
  char a[80] = "basicStiffness";
  const char *argvv[1];
  argvv[0] = a;

  DummyStream dummy;

  Response *theResponse = theElement->setResponse(argvv, argcc, dummy);
  if (theResponse == 0) {
    char buffer[] = "0.0";
    Tcl_SetResult(interp, buffer, TCL_VOLATILE);
    return TCL_OK;
  }

  theResponse->getResponse();
  Information &info = theResponse->getInformation();

  const Matrix &theMatrix = *(info.theMatrix);
  int nbf = theMatrix.noCols();

  char buffer[200];
  for (int i = 0; i < nbf; i++) {
    for (int j = 0; j < nbf; j++) {
      sprintf(buffer, "%12.8f ", theMatrix(i, j));
      Tcl_AppendResult(interp, buffer, NULL);
    }
  }

  delete theResponse;

  return TCL_OK;
}

// added by C.McGann, U.Washington
int
InitialStateAnalysis(ClientData clientData, Tcl_Interp *interp, int argc,
                     TCL_Char **argv)
{
  if (argc < 2) {
    opserr << "WARNING: Incorrect number of arguments for InitialStateAnalysis "
              "command"
           << endln;
    return TCL_ERROR;
  }

  if (strcmp(argv[1], "on") == 0) {
    opserr << "InitialStateAnalysis ON" << endln;

    // set global variable to true
    // FMK changes for parallel:
    // ops_InitialStateAnalysis = true;

    Parameter *theP = new InitialStateParameter(true);
    theDomain.addParameter(theP);
    delete theP;

    return TCL_OK;

  } else if (strcmp(argv[1], "off") == 0) {
    opserr << "InitialStateAnalysis OFF" << endln;

    // call revert to start to zero the displacements
    theDomain.revertToStart();

    // set global variable to false
    // FMK changes for parallel
    // ops_InitialStateAnalysis = false;
    Parameter *theP = new InitialStateParameter(false);
    theDomain.addParameter(theP);
    delete theP;

    return TCL_OK;

  } else {
    opserr << "WARNING: Incorrect arguments - want InitialStateAnalysis on, or "
              "InitialStateAnalysis off"
           << endln;

    return TCL_ERROR;
  }
}

int
computeGradients(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv)
{
#ifdef _RELIABILITY
  if (theSensitivityAlgorithm != 0)
    theSensitivityAlgorithm->computeSensitivities();
#endif
  return TCL_OK;
}
// AddingSensitivity:END //////////////////////////////////////

int
startTimer(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  if (theTimer == 0)
    theTimer = new Timer();

  theTimer->start();
  return TCL_OK;
}

int
stopTimer(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  if (theTimer == 0)
    return TCL_OK;

  theTimer->pause();
  opserr << *theTimer;
  return TCL_OK;
}

int
rayleighDamping(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  if (argc < 5) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - not enough "
              "arguments to command\n";
    return TCL_ERROR;
  }
  double alphaM, betaK, betaK0, betaKc;
  if (Tcl_GetDouble(interp, argv[1], &alphaM) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read alphaM? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[2], &betaK) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaK? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &betaK0) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaK0? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &betaKc) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaKc? \n";
    return TCL_ERROR;
  }

  Domain *the_domain = G3_getDomain(G3_getRuntime(interp));
  the_domain->setRayleighDampingFactors(alphaM, betaK, betaK0, betaKc);

  return TCL_OK;
}

int
setElementRayleighDampingFactors(ClientData clientData, Tcl_Interp *interp,
                                 int argc, TCL_Char **argv)
{
  if (argc < 6) {
    opserr << "WARNING setElementRayleighDampingFactors eleTag? alphaM? betaK? "
              "betaK0? betaKc? - not enough arguments to command\n";
    return TCL_ERROR;
  }
  int eleTag;
  double alphaM, betaK, betaK0, betaKc;

  if (Tcl_GetInt(interp, argv[1], &eleTag) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read eleTag? \n";
    return TCL_ERROR;
  }

  if (Tcl_GetDouble(interp, argv[2], &alphaM) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read alphaM? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &betaK) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaK? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &betaK0) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaK0? \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &betaKc) != TCL_OK) {
    opserr << "WARNING rayleigh alphaM? betaK? betaK0? betaKc? - could not "
              "read betaKc? \n";
    return TCL_ERROR;
  }

  Element *theEle = theDomain.getElement(eleTag);
  theEle->setRayleighDampingFactors(alphaM, betaK, betaK0, betaKc);
  return TCL_OK;
}

extern int TclAddMeshRegion(ClientData clientData, Tcl_Interp *interp, int argc,
                            TCL_Char **argv, Domain &theDomain);

int
addRegion(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  Domain *the_domain = G3_getDomain(G3_getRuntime(interp));
  OPS_ResetInputNoBuilder(clientData, interp, 1, argc, argv, the_domain);
  return TclAddMeshRegion(clientData, interp, argc, argv, theDomain);
}

int
logFile(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{

  if (argc < 2) {
    opserr << "WARNING logFile fileName? - no filename supplied\n";
    return TCL_ERROR;
  }
  openMode mode = OVERWRITE;
  bool echo = true;

  int cArg = 2;
  while (cArg < argc) {
    if (strcmp(argv[cArg], "-append") == 0)
      mode = APPEND;
    if (strcmp(argv[cArg], "-noEcho") == 0)
      echo = false;
    cArg++;
  }

  if (opserr.setFile(argv[1], mode, echo) < 0)
    opserr << "WARNING logFile " << argv[1] << " failed to set the file\n";

  const char *pwd = getInterpPWD(interp);
  simulationInfo.addOutputFile(argv[1], pwd);

  return TCL_OK;
}

int
setPrecision(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{

  if (argc < 2) {
    opserr << "WARNING setPrecision precision? - no precision value supplied\n";
    return TCL_ERROR;
  }
  int precision;
  if (Tcl_GetInt(interp, argv[1], &precision) != TCL_OK) {
    opserr << "WARNING setPrecision precision? - error reading precision value "
              "supplied\n";
    return TCL_ERROR;
  }
  opserr.setPrecision(precision);

  return TCL_OK;
}

int
exit(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  Tcl_Finalize();
  return TCL_OK;
}

int
getPID(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int pid = 0;
#ifdef _PARALLEL_INTERPRETERS
  if (theMachineBroker != 0)
    pid = theMachineBroker->getPID();
#endif

#ifdef _PARALLEL_PROCESSING
  if (theMachineBroker != 0)
    pid = theMachineBroker->getPID();
#endif

  // now we copy the value to the tcl string that is returned
  char buffer[30];
  sprintf(buffer, "%d", pid);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
getNP(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  int np = 1;
#ifdef _PARALLEL_INTERPRETERS
  if (theMachineBroker != 0)
    np = theMachineBroker->getNP();
#endif

#ifdef _PARALLEL_PROCESSING
  if (theMachineBroker != 0)
    np = theMachineBroker->getNP();
#endif

  // now we copy the value to the tcl string that is returned
  char buffer[30];
  sprintf(buffer, "%d", np);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
getNumElements(ClientData clientData, Tcl_Interp *interp, int argc,
               TCL_Char **argv)
{
  char buffer[20];

  sprintf(buffer, "%d ", theDomain.getNumElements());
  Tcl_AppendResult(interp, buffer, NULL);

  return TCL_OK;
}

int
getEleClassTags(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{

  if (argc == 1) {
    Element *theEle;
    ElementIter &eleIter = theDomain.getElements();

    char buffer[20];

    while ((theEle = eleIter()) != 0) {
      sprintf(buffer, "%d ", theEle->getClassTag());
      Tcl_AppendResult(interp, buffer, NULL);
    }
  } else if (argc == 2) {
    int eleTag;

    if (Tcl_GetInt(interp, argv[1], &eleTag) != TCL_OK) {
      opserr << "WARNING getParamValue -- could not read paramTag \n";
      return TCL_ERROR;
    }

    Element *theEle = theDomain.getElement(eleTag);

    char buffer[20];

    sprintf(buffer, "%d ", theEle->getClassTag());
    Tcl_AppendResult(interp, buffer, NULL);

  } else {
    opserr << "WARNING want - getEleClassTags <eleTag?>\n" << endln;
    return TCL_ERROR;
  }

  return TCL_OK;
}

int
getEleLoadClassTags(ClientData clientData, Tcl_Interp *interp, int argc,
                    TCL_Char **argv)
{

  if (argc == 1) {
    LoadPattern *thePattern;
    LoadPatternIter &thePatterns = theDomain.getLoadPatterns();

    char buffer[20];

    while ((thePattern = thePatterns()) != 0) {
      ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
      ElementalLoad *theLoad;

      while ((theLoad = theEleLoads()) != 0) {
        sprintf(buffer, "%d ", theLoad->getClassTag());
        Tcl_AppendResult(interp, buffer, NULL);
      }
    }

  } else if (argc == 2) {
    int patternTag;

    if (Tcl_GetInt(interp, argv[1], &patternTag) != TCL_OK) {
      opserr << "WARNING getEleLoadClassTags -- could not read patternTag\n";
      return TCL_ERROR;
    }

    LoadPattern *thePattern = theDomain.getLoadPattern(patternTag);
    if (thePattern == nullptr) {
      opserr << "ERROR load pattern with tag " << patternTag
             << " not found in domain -- getEleLoadClassTags\n";
      return TCL_ERROR;
    }

    ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
    ElementalLoad *theLoad;

    char buffer[20];

    while ((theLoad = theEleLoads()) != 0) {
      sprintf(buffer, "%d ", theLoad->getClassTag());
      Tcl_AppendResult(interp, buffer, NULL);
    }

  } else {
    opserr << "WARNING want - getEleLoadClassTags <patternTag?>\n" << endln;
    return TCL_ERROR;
  }

  return TCL_OK;
}

int
getEleLoadTags(ClientData clientData, Tcl_Interp *interp, int argc,
               TCL_Char **argv)
{

  if (argc == 1) {
    LoadPattern *thePattern;
    LoadPatternIter &thePatterns = theDomain.getLoadPatterns();

    char buffer[20];

    while ((thePattern = thePatterns()) != 0) {
      ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
      ElementalLoad *theLoad;

      while ((theLoad = theEleLoads()) != 0) {
        sprintf(buffer, "%d ", theLoad->getElementTag());
        Tcl_AppendResult(interp, buffer, NULL);
      }
    }

  } else if (argc == 2) {
    int patternTag;

    if (Tcl_GetInt(interp, argv[1], &patternTag) != TCL_OK) {
      opserr << "WARNING getEleLoadTags -- could not read patternTag \n";
      return TCL_ERROR;
    }

    LoadPattern *thePattern = theDomain.getLoadPattern(patternTag);
    if (thePattern == nullptr) {
      opserr << "ERROR load pattern with tag " << patternTag
             << " not found in domain -- getEleLoadTags\n";
      return TCL_ERROR;
    }

    ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
    ElementalLoad *theLoad;

    char buffer[20];

    while ((theLoad = theEleLoads()) != 0) {
      sprintf(buffer, "%d ", theLoad->getElementTag());
      Tcl_AppendResult(interp, buffer, NULL);
    }

  } else {
    opserr << "WARNING want - getEleLoadTags <patternTag?>\n" << endln;
    return TCL_ERROR;
  }

  return TCL_OK;
}

int
getEleLoadData(ClientData clientData, Tcl_Interp *interp, int argc,
               TCL_Char **argv)
{

  if (argc == 1) {
    LoadPattern *thePattern;
    LoadPatternIter &thePatterns = theDomain.getLoadPatterns();

    char buffer[40];
    int typeEL;

    while ((thePattern = thePatterns()) != 0) {
      ElementalLoadIter &theEleLoads = thePattern->getElementalLoads();
      ElementalLoad *theLoad;

      while ((theLoad = theEleLoads()) != 0) {
        const Vector &eleLoadData = theLoad->getData(typeEL, 1.0);

        int eleLoadDataSize = eleLoadData.Size();
        opserr << "eleLoadDataSize: " << eleLoadDataSize << "\n";
        for (int i = 0; i < eleLoadDataSize; i++) {
          sprintf(buffer, "%35.20f ", eleLoadData(i));
          Tcl_AppendResult(interp, buffer, NULL);
        }
      }
    }

  } else if (argc == 2) {
    int patternTag;

    if (Tcl_GetInt(interp, argv[1], &patternTag) != TCL_OK) {
      opserr << "WARNING getEleLoadData -- could not read patternTag \n";
      return TCL_ERROR;
    }

    LoadPattern *thePattern = theDomain.getLoadPattern(patternTag);
    if (thePattern == nullptr) {
      opserr << "ERROR load pattern with tag " << patternTag
             << " not found in domain -- getEleLoadData\n";
      return TCL_ERROR;
    }

    ElementalLoadIter theEleLoads = thePattern->getElementalLoads();
    ElementalLoad *theLoad;

    int typeEL;
    char buffer[40];

    while ((theLoad = theEleLoads()) != 0) {
      const Vector &eleLoadData = theLoad->getData(typeEL, 1.0);

      int eleLoadDataSize = eleLoadData.Size();
      for (int i = 0; i < eleLoadDataSize; i++) {
        sprintf(buffer, "%35.20f ", eleLoadData(i));
        Tcl_AppendResult(interp, buffer, NULL);
      }
    }

  } else {
    opserr << "WARNING want - getEleLoadTags <patternTag?>\n" << endln;
    return TCL_ERROR;
  }

  return TCL_OK;
}

int
getEleTags(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  Element *theEle;
  ElementIter &eleIter = theDomain.getElements();

  char buffer[20];

  while ((theEle = eleIter()) != 0) {
    sprintf(buffer, "%d ", theEle->getTag());
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
getNodeTags(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  G3_Runtime *rt  = G3_getRuntime(interp);
  Domain *the_domain = G3_getDomain(rt);
  Node *node;
  if (the_domain==nullptr)
    return TCL_ERROR;

  NodeIter &nodeIter = the_domain->getNodes();

  char buffer[20];

  while ((node = nodeIter()) != 0) {
    sprintf(buffer, "%d ", node->getTag());
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
getParamTags(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  Parameter *theEle;
  ParameterIter &eleIter = theDomain.getParameters();

  char buffer[20];

  while ((theEle = eleIter()) != 0) {
    sprintf(buffer, "%d ", theEle->getTag());
    Tcl_AppendResult(interp, buffer, NULL);
  }

  return TCL_OK;
}

int
getParamValue(ClientData clientData, Tcl_Interp *interp, int argc,
              TCL_Char **argv)
{
  if (argc < 2) {
    opserr << "Insufficient arguments to getParamValue" << endln;
    return TCL_ERROR;
  }

  int paramTag;

  if (Tcl_GetInt(interp, argv[1], &paramTag) != TCL_OK) {
    opserr << "WARNING getParamValue -- could not read paramTag \n";
    return TCL_ERROR;
  }

  Parameter *theEle = theDomain.getParameter(paramTag);

  char buffer[40];

  sprintf(buffer, "%35.20f", theEle->getValue());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
sdfResponse(ClientData clientData, Tcl_Interp *interp, int argc,
            TCL_Char **argv)
{
  if (argc < 9) {
    opserr << "Insufficient arguments to sdfResponse" << endln;
    return TCL_ERROR;
  }

  double m, zeta, k, Fy, alpha, dtF, dt;
  if (Tcl_GetDouble(interp, argv[1], &m) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read mass \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[2], &zeta) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read zeta \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[3], &k) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read k \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[4], &Fy) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read Fy \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[5], &alpha) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read alpha \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[6], &dtF) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read dtF \n";
    return TCL_ERROR;
  }
  if (Tcl_GetDouble(interp, argv[8], &dt) != TCL_OK) {
    opserr << "WARNING sdfResponse -- could not read dt \n";
    return TCL_ERROR;
  }
  double uresidual = 0.0;
  double umaxprev = 0.0;
  if (argc > 9) {
    if (Tcl_GetDouble(interp, argv[9], &uresidual) != TCL_OK) {
      opserr << "WARNING sdfResponse -- could not read uresidual \n";
      return TCL_ERROR;
    }
    if (Tcl_GetDouble(interp, argv[10], &umaxprev) != TCL_OK) {
      opserr << "WARNING sdfResponse -- could not read umaxprev \n";
      return TCL_ERROR;
    }
  }

  double gamma = 0.5;
  double beta = 0.25;
  double tol = 1.0e-8;
  int maxIter = 10;

  std::ifstream infile(argv[7]);

  double c = zeta * 2 * sqrt(k * m);
  double Hkin = alpha / (1.0 - alpha) * k;

  double p0 = 0.0;
  double u0 = uresidual;
  double v0 = 0.0;
  double fs0 = 0.0;
  double a0 = (p0 - c * v0 - fs0) / m;

  double a1 = m / (beta * dt * dt) + (gamma / (beta * dt)) * c;
  double a2 = m / (beta * dt) + (gamma / beta - 1.0) * c;
  double a3 = (0.5 / beta - 1.0) * m + dt * (0.5 * gamma / beta - 1.0) * c;

  double au = 1.0 / (beta * dt * dt);
  double av = 1.0 / (beta * dt);
  double aa = 0.5 / beta - 1.0;

  double vu = gamma / (beta * dt);
  double vv = 1.0 - gamma / beta;
  double va = dt * (1 - 0.5 * gamma / beta);

  double kT0 = k;

  double umax = fabs(umaxprev);
  double amax = 0.0;
  double tamax = 0.0;
  double up = uresidual;
  double up0 = up;
  int i = 0;
  double ft, u, du, v, a, fs, zs, ftrial, kT, kTeff, dg, phat, R, R0, accel;
  while (infile >> ft) {
    i++;

    u = u0;

    fs = fs0;
    kT = kT0;
    up = up0;

    phat = ft + a1 * u0 + a2 * v0 + a3 * a0;

    R = phat - fs - a1 * u;
    R0 = R;
    if (R0 == 0.0) {
      R0 = 1.0;
    }

    int iter = 0;

    while (iter < maxIter && fabs(R / R0) > tol) {
      iter++;

      kTeff = kT + a1;

      du = R / kTeff;

      u = u + du;

      fs = k * (u - up0);
      zs = fs - Hkin * up0;
      ftrial = fabs(zs) - Fy;
      if (ftrial > 0) {
        dg = ftrial / (k + Hkin);
        if (fs < 0) {
          fs = fs + dg * k;
          up = up0 - dg;
        } else {
          fs = fs - dg * k;
          up = up0 + dg;
        }
        kT = k * Hkin / (k + Hkin);
      } else {
        kT = k;
      }

      R = phat - fs - a1 * u;
    }

    v = vu * (u - u0) + vv * v0 + va * a0;
    a = au * (u - u0) - av * v0 - aa * a0;

    u0 = u;
    v0 = v;
    a0 = a;
    fs0 = fs;
    kT0 = kT;
    up0 = up;

    if (fabs(u) > umax) {
      umax = fabs(u);
    }
    if (fabs(a) > amax) {
      amax = fabs(a);
      tamax = iter * dt;
    }
  }

  infile.close();

  char buffer[80];
  sprintf(buffer, "%f %f %f %f %f", umax, u, up, amax, tamax);

  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
opsBarrier(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
#ifdef _PARALLEL_INTERPRETERS
  return MPI_Barrier(MPI_COMM_WORLD);
#endif

  return TCL_OK;
}

int
opsSend(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
#ifdef _PARALLEL_INTERPRETERS
  if (argc < 2)
    return TCL_OK;

  int otherPID = -1;
  int myPID = theMachineBroker->getPID();
  int np = theMachineBroker->getNP();
  const char *dataToSend = argv[argc - 1];
  int msgLength = strlen(dataToSend) + 1;

  const char *gMsg = dataToSend;
  //  strcpy(gMsg, dataToSend);

  if (strcmp(argv[1], "-pid") == 0 && argc > 3) {

    if (Tcl_GetInt(interp, argv[2], &otherPID) != TCL_OK) {
      opserr << "send -pid pid? data? - pid: " << argv[2] << " invalid\n";
      return TCL_ERROR;
    }

    if (otherPID > -1 && otherPID != myPID && otherPID < np) {

      MPI_Send((void *)(&msgLength), 1, MPI_INT, otherPID, 0, MPI_COMM_WORLD);
      MPI_Send((void *)gMsg, msgLength, MPI_CHAR, otherPID, 1, MPI_COMM_WORLD);

    } else {
      opserr << "send -pid pid? data? - pid: " << otherPID << " invalid\n";
      return TCL_ERROR;
    }

  } else {
    if (myPID == 0) {
      MPI_Bcast((void *)(&msgLength), 1, MPI_INT, 0, MPI_COMM_WORLD);
      MPI_Bcast((void *)gMsg, msgLength, MPI_CHAR, 0, MPI_COMM_WORLD);
    } else {
      opserr << "send data - only process 0 can do a broadcast - you may need "
                "to kill the application";
      return TCL_ERROR;
    }
  }

#endif

  return TCL_OK;
}

int
opsRecv(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
#ifdef _PARALLEL_INTERPRETERS
  if (argc < 2)
    return TCL_OK;

  int otherPID = 0;
  int myPID = theMachineBroker->getPID();
  int np = theMachineBroker->getNP();
  TCL_Char *varToSet = argv[argc - 1];

  int msgLength = 0;
  char *gMsg = 0;

  if (strcmp(argv[1], "-pid") == 0 && argc > 3) {

    bool fromAny = false;

    if ((strcmp(argv[2], "ANY") == 0) || (strcmp(argv[2], "ANY_SOURCE") == 0) ||
        (strcmp(argv[2], "MPI_ANY_SOURCE") == 0)) {
      fromAny = true;
    } else {
      if (Tcl_GetInt(interp, argv[2], &otherPID) != TCL_OK) {
        opserr << "recv -pid pid? data? - pid: " << argv[2] << " invalid\n";
        return TCL_ERROR;
      }
    }

    if (otherPID > -1 && otherPID < np) {
      MPI_Status status;

      if (fromAny == false)
        if (myPID != otherPID)
          MPI_Recv((void *)(&msgLength), 1, MPI_INT, otherPID, 0,
                   MPI_COMM_WORLD, &status);
        else {
          opserr << "recv -pid pid? data? - " << otherPID
                 << " cant receive from self!\n";
          return TCL_ERROR;
        }
      else {
        MPI_Recv((void *)(&msgLength), 1, MPI_INT, MPI_ANY_SOURCE, 0,
                 MPI_COMM_WORLD, &status);
        otherPID = status.MPI_SOURCE;
      }

      if (msgLength > 0) {
        gMsg = new char[msgLength];

        MPI_Recv((void *)gMsg, msgLength, MPI_CHAR, otherPID, 1, MPI_COMM_WORLD,
                 &status);

        Tcl_SetVar(interp, varToSet, gMsg, TCL_LEAVE_ERR_MSG);
      }

    } else {
      opserr << "recv -pid pid? data? - " << otherPID << " invalid\n";
      return TCL_ERROR;
    }
  } else {

    if (myPID != 0) {
      MPI_Bcast((void *)(&msgLength), 1, MPI_INT, 0, MPI_COMM_WORLD);

      if (msgLength > 0) {
        gMsg = new char[msgLength];

        MPI_Bcast((void *)gMsg, msgLength, MPI_CHAR, 0, MPI_COMM_WORLD);

        Tcl_SetVar(interp, varToSet, gMsg, TCL_LEAVE_ERR_MSG);
      }

    } else {
      opserr << "recv data - only process 0 can do a broadcast - you may need "
                "to kill the application";
      return TCL_ERROR;
    }
  }

#endif

  return TCL_OK;
}

int
defaultUnits(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  if (argc < 7) {
    opserr << "defaultUnits - missing a unit type want: defaultUnits -Force "
              "type? -Length type? -Time type?\n";
    return -1;
  }

  const char *force = 0;
  const char *length = 0;
  const char *time = 0;
  const char *temperature = "N/A";

  int count = 1;
  while (count < argc) {
    if ((strcmp(argv[count], "-force") == 0) ||
        (strcmp(argv[count], "-Force") == 0) ||
        (strcmp(argv[count], "-FORCE") == 0)) {
      force = argv[count + 1];
    } else if ((strcmp(argv[count], "-length") == 0) ||
               (strcmp(argv[count], "-Length") == 0) ||
               (strcmp(argv[count], "-LENGTH") == 0)) {
      length = argv[count + 1];
    } else if ((strcmp(argv[count], "-time") == 0) ||
               (strcmp(argv[count], "-Time") == 0) ||
               (strcmp(argv[count], "-TIME") == 0)) {
      time = argv[count + 1];
    } else if ((strcmp(argv[count], "-temperature") == 0) ||
               (strcmp(argv[count], "-Temperature") == 0) ||
               (strcmp(argv[count], "-TEMPERATURE") == 0) ||
               (strcmp(argv[count], "-temp") == 0) ||
               (strcmp(argv[count], "-Temp") == 0) ||
               (strcmp(argv[count], "-TEMP") == 0)) {
      temperature = argv[count + 1];
    } else {
      opserr << "defaultUnits - unrecognized unit: " << argv[count]
             << " want: defaultUnits -Force type? -Length type? -Time type?\n";
      return -1;
    }
    count += 2;
  }

  if (length == 0 || force == 0 || time == 0) {
    opserr << "defaultUnits - missing a unit type want: defaultUnits -Force "
              "type? -Length type? -Time type?\n";
    return -1;
  }

  double lb, kip, n, kn, mn, kgf, tonf;
  double in, ft, mm, cm, m;
  double sec, msec;

  if ((strcmp(force, "lb") == 0) || (strcmp(force, "lbs") == 0)) {
    lb = 1.0;
  } else if ((strcmp(force, "kip") == 0) || (strcmp(force, "kips") == 0)) {
    lb = 0.001;
  } else if ((strcmp(force, "N") == 0)) {
    lb = 4.4482216152605;
  } else if ((strcmp(force, "kN") == 0) || (strcmp(force, "KN") == 0) ||
             (strcmp(force, "kn") == 0)) {
    lb = 0.0044482216152605;
  } else if ((strcmp(force, "mN") == 0) || (strcmp(force, "MN") == 0) ||
             (strcmp(force, "mn") == 0)) {
    lb = 0.0000044482216152605;
  } else if ((strcmp(force, "kgf") == 0)) {
    lb = 4.4482216152605 / 9.80665;
  } else if ((strcmp(force, "tonf") == 0)) {
    lb = 4.4482216152605 / 9.80665 / 1000.0;
  } else {
    lb = 1.0;
    opserr << "defaultUnits - unknown force type, valid options: lb, kip, N, "
              "kN, MN, kgf, tonf\n";
    return TCL_ERROR;
  }

  if ((strcmp(length, "in") == 0) || (strcmp(length, "inch") == 0)) {
    in = 1.0;
  } else if ((strcmp(length, "ft") == 0) || (strcmp(length, "feet") == 0)) {
    in = 1.0 / 12.0;
  } else if ((strcmp(length, "mm") == 0)) {
    in = 25.4;
  } else if ((strcmp(length, "cm") == 0)) {
    in = 2.54;
  } else if ((strcmp(length, "m") == 0)) {
    in = 0.0254;
  } else {
    in = 1.0;
    opserr << "defaultUnits - unknown length type, valid options: in, ft, mm, "
              "cm, m\n";
    return TCL_ERROR;
  }

  if ((strcmp(time, "sec") == 0) || (strcmp(time, "Sec") == 0)) {
    sec = 1.0;
  } else if ((strcmp(time, "msec") == 0) || (strcmp(time, "mSec") == 0)) {
    sec = 1000.0;
  } else {
    sec = 1.0;
    opserr << "defaultUnits - unknown time type, valid options: sec, msec\n";
    return TCL_ERROR;
  }

  kip = lb / 0.001;
  n = lb / 4.4482216152605;
  kn = lb / 0.0044482216152605;
  mn = lb / 0.0000044482216152605;
  kgf = lb / (4.4482216152605 / 9.80665);
  tonf = lb / (4.4482216152605 / 9.80665 / 1000.0);

  ft = in * 12.0;
  mm = in / 25.4;
  cm = in / 2.54;
  m = in / 0.0254;

  msec = sec * 0.001;

  char string[50];

  sprintf(string, "set lb %.18e", lb);
  Tcl_Eval(interp, string);
  sprintf(string, "set lbf %.18e", lb);
  Tcl_Eval(interp, string);
  sprintf(string, "set kip %.18e", kip);
  Tcl_Eval(interp, string);
  sprintf(string, "set N %.18e", n);
  Tcl_Eval(interp, string);
  sprintf(string, "set kN %.18e", kn);
  Tcl_Eval(interp, string);
  sprintf(string, "set Newton %.18e", n);
  Tcl_Eval(interp, string);
  sprintf(string, "set kNewton %.18e", kn);
  Tcl_Eval(interp, string);
  sprintf(string, "set MN %.18e", mn);
  Tcl_Eval(interp, string);
  sprintf(string, "set kgf %.18e", kgf);
  Tcl_Eval(interp, string);
  sprintf(string, "set tonf %.18e", tonf);
  Tcl_Eval(interp, string);

  sprintf(string, "set in %.18e", in);
  Tcl_Eval(interp, string);
  sprintf(string, "set inch %.18e", in);
  Tcl_Eval(interp, string);
  sprintf(string, "set ft %.18e", ft);
  Tcl_Eval(interp, string);
  sprintf(string, "set mm %.18e", mm);
  Tcl_Eval(interp, string);
  sprintf(string, "set cm %.18e", cm);
  Tcl_Eval(interp, string);
  sprintf(string, "set m  %.18e", m);
  Tcl_Eval(interp, string);
  sprintf(string, "set meter  %.18e", m);
  Tcl_Eval(interp, string);

  sprintf(string, "set sec %.18e", sec);
  Tcl_Eval(interp, string);
  sprintf(string, "set msec %.18e", msec);
  Tcl_Eval(interp, string);

  double g = 32.174049 * ft / (sec * sec);
  sprintf(string, "set g %.18e", g);
  Tcl_Eval(interp, string);
  sprintf(string, "set kg %.18e", n * sec * sec / m);
  Tcl_Eval(interp, string);
  sprintf(string, "set Mg %.18e", 1e3 * n * sec * sec / m);
  Tcl_Eval(interp, string);
  sprintf(string, "set slug %.18e", lb * sec * sec / ft);
  Tcl_Eval(interp, string);
  sprintf(string, "set Pa %.18e", n / (m * m));
  Tcl_Eval(interp, string);
  sprintf(string, "set kPa %.18e", 1e3 * n / (m * m));
  Tcl_Eval(interp, string);
  sprintf(string, "set MPa %.18e", 1e6 * n / (m * m));
  Tcl_Eval(interp, string);
  sprintf(string, "set psi %.18e", lb / (in * in));
  Tcl_Eval(interp, string);
  sprintf(string, "set ksi %.18e", kip / (in * in));
  Tcl_Eval(interp, string);
  sprintf(string, "set psf %.18e", lb / (ft * ft));
  Tcl_Eval(interp, string);
  sprintf(string, "set ksf %.18e", kip / (ft * ft));
  Tcl_Eval(interp, string);
  sprintf(string, "set pcf %.18e", lb / (ft * ft * ft));
  Tcl_Eval(interp, string);
  sprintf(string, "set in2 %.18e", in * in);
  Tcl_Eval(interp, string);
  sprintf(string, "set ft2 %.18e", ft * ft);
  Tcl_Eval(interp, string);
  sprintf(string, "set mm2 %.18e", mm * mm);
  Tcl_Eval(interp, string);
  sprintf(string, "set cm2 %.18e", cm * cm);
  Tcl_Eval(interp, string);
  sprintf(string, "set m2 %.18e", m * m);
  Tcl_Eval(interp, string);
  sprintf(string, "set in4 %.18e", in * in * in * in);
  Tcl_Eval(interp, string);
  sprintf(string, "set ft4 %.18e", ft * ft * ft * ft);
  Tcl_Eval(interp, string);
  sprintf(string, "set mm4 %.18e", mm * mm * mm * mm);
  Tcl_Eval(interp, string);
  sprintf(string, "set cm4 %.18e", cm * cm * cm * cm);
  Tcl_Eval(interp, string);
  sprintf(string, "set m4 %.18e", m * m * m * m);
  Tcl_Eval(interp, string);
  sprintf(string, "set pi %.18e", 2.0 * asin(1.0));
  Tcl_Eval(interp, string);
  sprintf(string, "set PI %.18e", 2.0 * asin(1.0));
  Tcl_Eval(interp, string);

  int res = simulationInfo.setForceUnit(force);
  res += simulationInfo.setLengthUnit(length);
  res += simulationInfo.setTimeUnit(time);
  res += simulationInfo.setTemperatureUnit(temperature);

  return res;
}

const char *
getInterpPWD(Tcl_Interp *interp)
{
  static char *pwd = 0;

  if (pwd != 0)
    delete[] pwd;

#ifdef _TCL84
  Tcl_Obj *cwd = Tcl_FSGetCwd(interp);
  if (cwd != NULL) {
    int length;
    const char *objPWD = Tcl_GetStringFromObj(cwd, &length);
    pwd = new char[length + 1];
    strcpy(pwd, objPWD);
    Tcl_DecrRefCount(cwd);
  }
#else

  Tcl_DString buf;
  const char *objPWD = Tcl_GetCwd(interp, &buf);

  pwd = new char[strlen(objPWD) + 1];
  strcpy(pwd, objPWD);

  Tcl_DStringFree(&buf);

#endif
  return pwd;
}

int
OpenSeesExit(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  theDomain.clearAll();

#ifdef _PARALLEL_PROCESSING
  //
  // mpi clean up
  //
  if (theMachineBroker != 0) {
    theMachineBroker->shutdown();
    fprintf(stderr, "Process Terminating\n");
  }
  MPI_Finalize();
#endif

#ifdef _PARALLEL_INTERPRETERS
  //
  // mpi clean up
  //
  if (theMachineBroker != 0) {
    theMachineBroker->shutdown();
    fprintf(stderr, "Process Terminating\n");
  }
  MPI_Finalize();
#endif

  if (simulationInfoOutputFilename != 0) {
    simulationInfo.end();
    XmlFileStream simulationInfoOutputFile;
    simulationInfoOutputFile.setFile(simulationInfoOutputFilename);
    simulationInfoOutputFile.open();
    simulationInfoOutputFile << simulationInfo;
    simulationInfoOutputFile.close();
    simulationInfoOutputFilename = 0;
  }

  int returnCode = 0;
  if (argc > 1) {
    if (Tcl_GetInt(interp, argv[1], &returnCode) != TCL_OK)
      opserr << "WARNING: OpenSeesExit - failed to read return code\n";
  }
  Tcl_Exit(returnCode);

  return 0;
}

int
stripOpenSeesXML(ClientData clientData, Tcl_Interp *interp, int argc,
                 TCL_Char **argv)
{

  if (argc < 3) {
    opserr << "ERROR incorrect # args - stripXML input.xml output.dat "
              "<output.xml>\n";
    return -1;
  }

  const char *inputFile = argv[1];
  const char *outputDataFile = argv[2];
  const char *outputDescriptiveFile = 0;

  if (argc == 4)
    outputDescriptiveFile = argv[3];

  // open files
  ifstream theInputFile;
  theInputFile.open(inputFile, ios::in);
  if (theInputFile.bad()) {
    opserr << "stripXML - error opening input file: " << inputFile << endln;
    return -1;
  }

  ofstream theOutputDataFile;
  theOutputDataFile.open(outputDataFile, ios::out);
  if (theOutputDataFile.bad()) {
    opserr << "stripXML - error opening input file: " << outputDataFile
           << endln;
    return -1;
  }

  ofstream theOutputDescriptiveFile;
  if (outputDescriptiveFile != 0) {
    theOutputDescriptiveFile.open(outputDescriptiveFile, ios::out);
    if (theOutputDescriptiveFile.bad()) {
      opserr << "stripXML - error opening input file: " << outputDescriptiveFile
             << endln;
      return -1;
    }
  }

  string line;
  bool spitData = false;
  while (!theInputFile.eof()) {
    getline(theInputFile, line);
    const char *inputLine = line.c_str();

    if (spitData == true) {
      if (strstr(inputLine, "</Data>") != 0)
        spitData = false;
      else
        ; //	theOutputDataFile << line << endln;
    } else {
      const char *inputLine = line.c_str();
      if (strstr(inputLine, "<Data>") != 0)
        spitData = true;
      else if (outputDescriptiveFile != 0)
        ; // theOutputDescriptiveFile << line << endln;
    }
  }

  theInputFile.close();
  theOutputDataFile.close();

  if (outputDescriptiveFile != 0)
    theOutputDescriptiveFile.close();

  return 0;
}

extern int binaryToText(const char *inputFilename, const char *outputFilename);
extern int textToBinary(const char *inputFilename, const char *outputFilename);

int
convertBinaryToText(ClientData clientData, Tcl_Interp *interp, int argc,
                    TCL_Char **argv)
{
  if (argc < 3) {
    opserr << "ERROR incorrect # args - convertBinaryToText inputFile "
              "outputFile\n";
    return -1;
  }

  const char *inputFile = argv[1];
  const char *outputFile = argv[2];

  return binaryToText(inputFile, outputFile);
}

int
convertTextToBinary(ClientData clientData, Tcl_Interp *interp, int argc,
                    TCL_Char **argv)
{
  if (argc < 3) {
    opserr << "ERROR incorrect # args - convertTextToBinary inputFile "
              "outputFile\n";
    return -1;
  }

  const char *inputFile = argv[1];
  const char *outputFile = argv[2];

  return textToBinary(inputFile, outputFile);
}

int
domainChange(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  theDomain.domainChange();
  return TCL_OK;
}

int
record(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  theDomain.record(false);
  return TCL_OK;
}

extern int peerSearchNGA(const char *eq, const char *soilType,
                         const char *fault, const char *magLo,
                         const char *magHi, const char *distLo,
                         const char *distHi, const char *vsLo, const char *vsHi,
                         const char *pgaLo, const char *pgaHi,
                         const char *latSW, const char *latNE,
                         const char *lngSW, const char *lngNW,
                         StringContainer &recordNames);

int
peerNGA(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  StringContainer ngaRecordNames;
  const char *eq = 0;
  const char *soilType = 0;
  const char *fault = 0;
  const char *magLo = 0;
  const char *magHi = 0;
  const char *distLo = 0;
  const char *distHi = 0;
  const char *vsLo = 0;
  const char *vsHi = 0;
  const char *pgaLo = 0;
  const char *pgaHi = 0;
  const char *latSW = 0;
  const char *latNE = 0;
  const char *lngSW = 0;
  const char *lngNW = 0;

  int currentArg = 1;
  while (currentArg + 1 < argc) {
    if (strcmp(argv[currentArg], "-eq") == 0) {
      eq = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-fault") == 0) {
      fault = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-soil") == 0) {
      soilType = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-magLo") == 0) {
      magLo = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-magHi") == 0) {
      magHi = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-distLo") == 0) {
      distLo = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-distHi") == 0) {
      distHi = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-vsLo") == 0) {
      vsLo = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-vsHi") == 0) {
      vsHi = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-pgaLo") == 0) {
      pgaLo = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-pgaHi") == 0) {
      pgaHi = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-latSW") == 0) {
      latSW = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-latNE") == 0) {
      latNE = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-lngSW") == 0) {
      lngSW = argv[currentArg + 1];
    } else if (strcmp(argv[currentArg], "-lngNW") == 0) {
      lngNW = argv[currentArg + 1];
    }
    // unrecognized
    currentArg += 2;
  }

  peerSearchNGA(eq, soilType, fault, magLo, magHi, distLo, distHi, vsLo, vsHi,
                pgaLo, pgaHi, latSW, latNE, lngSW, lngNW, ngaRecordNames);

  int numStrings = ngaRecordNames.getNumStrings();
  for (int i = 0; i < numStrings; i++) {
    Tcl_AppendResult(interp, ngaRecordNames.getString(i), NULL);
    Tcl_AppendResult(interp, " ", NULL);
  }

  return TCL_OK;
}

int
totalCPU(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theAlgorithm == 0)
    return TCL_ERROR;

  sprintf(buffer, "%f", theAlgorithm->getTotalTimeCPU());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
solveCPU(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theAlgorithm == 0)
    return TCL_ERROR;

  sprintf(buffer, "%f", theAlgorithm->getSolveTimeCPU());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
accelCPU(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theAlgorithm == 0)
    return TCL_ERROR;

  sprintf(buffer, "%f", theAlgorithm->getAccelTimeCPU());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
numFact(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theAlgorithm == 0)
    return TCL_ERROR;

  sprintf(buffer, "%d", theAlgorithm->getNumFactorizations());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
systemSize(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theSOE == 0) {
    sprintf(buffer, "NO SYSTEM SET");
    return TCL_OK;
  }

  sprintf(buffer, "%d", theSOE->getNumEqn());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
numIter(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  if (theAlgorithm == 0)
    return TCL_ERROR;

  sprintf(buffer, "%d", theAlgorithm->getNumIterations());
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

int
elementActivate(ClientData clientData, Tcl_Interp *interp, int argc,
                TCL_Char **argv)
{
  int eleTag;
  int argLoc = 1;
  int Nelements = argc;
  ID activate_us(0, Nelements);

  while (argLoc < argc && Tcl_GetInt(interp, argv[argLoc], &eleTag) == TCL_OK) {
    activate_us.insert(eleTag);
    ++argLoc;
  }

  theDomain.activateElements(activate_us);

  return TCL_OK;
}

int
elementDeactivate(ClientData clientData, Tcl_Interp *interp, int argc,
                  TCL_Char **argv)
{

  int eleTag;
  int argLoc = 1;
  int Nelements = argc;
  ID deactivate_us(0, Nelements);

  while (argLoc < argc && Tcl_GetInt(interp, argv[argLoc], &eleTag) == TCL_OK) {
    deactivate_us.insert(eleTag);
    ++argLoc;
  }

  theDomain.deactivateElements(deactivate_us);
  return TCL_OK;
}

int
version(ClientData clientData, Tcl_Interp *interp, int argc, TCL_Char **argv)
{
  char buffer[20];

  sprintf(buffer, "%s", OPS_VERSION);
  Tcl_SetResult(interp, buffer, TCL_VOLATILE);

  return TCL_OK;
}

extern "C" int
OpenSeesParseArgv(int argc, char **argv)
{
  if (argc > 1) {
    int currentArg = 1;
    while (currentArg < argc && argv[currentArg] != NULL) {

      if ((strcmp(argv[currentArg], "-par") == 0) ||
          (strcmp(argv[currentArg], "-Par") == 0)) {

        if (argc > (currentArg + 2)) {

          char *parName = argv[currentArg + 1];
          char *parValue = argv[currentArg + 2];

          // add a OpenSeesTcl_Parameter to end of list of parameters
          OpenSeesTcl_Parameter *nextParam = new OpenSeesTcl_Parameter;
          nextParam->name = new char[strlen(parName) + 1];
          strcpy(nextParam->name, parName);
          nextParam->values = 0;

          if (theParameters == 0)
            theParameters = nextParam;
          if (endParameters != 0)
            endParameters->next = nextParam;
          nextParam->next = 0;
          endParameters = nextParam;

          // now open par values files to create the values
          char nextLine[1000];
          FILE *valueFP = fopen(parValue, "r");
          if (valueFP != 0) {
            OpenSeesTcl_ParameterValues *endValues = 0;

            while (fscanf(valueFP, "%s", nextLine) != EOF) {

              OpenSeesTcl_ParameterValues *nextValue =
                  new OpenSeesTcl_ParameterValues;
              nextValue->value = new char[strlen(nextLine) + 1];
              strcpy(nextValue->value, nextLine);

              if (nextParam->values == 0) {
                nextParam->values = nextValue;
              }
              if (endValues != 0)
                endValues->next = nextValue;
              endValues = nextValue;
              nextValue->next = 0;
            }
            fclose(valueFP);
          } else {

            OpenSeesTcl_ParameterValues *nextValue =
                new OpenSeesTcl_ParameterValues;
            nextValue->value = new char[strlen(parValue) + 1];

            strcpy(nextValue->value, parValue);

            nextParam->values = nextValue;
            nextValue->next = 0;
          }
          numParam++;
        }
        currentArg += 3;
      } else if ((strcmp(argv[currentArg], "-info") == 0) ||
                 (strcmp(argv[currentArg], "-INFO") == 0)) {
        if (argc > (currentArg + 1)) {
          simulationInfoOutputFilename = argv[currentArg + 1];
        }
        currentArg += 2;
      } else
        currentArg++;
    }
  }
  if (numParam != 0) {
    paramNames = new char *[numParam];
    paramValues = new char *[numParam];
  }
  return numParam;
}

extern "C" int
EvalFileWithParameters(Tcl_Interp *interp, char *tclStartupFileScript,
                       OpenSeesTcl_Parameter *theInputParameters,
                       int currentParam, int rank, int np)
{
  if (theInputParameters == 0)
    theInputParameters = theParameters;

  if (currentParam < numParam) {
    OpenSeesTcl_Parameter *theCurrentParam = theInputParameters;
    OpenSeesTcl_Parameter *theNextParam = theParameters->next;
    char *paramName = theCurrentParam->name;
    paramNames[currentParam] = paramName;

    OpenSeesTcl_ParameterValues *theValue = theCurrentParam->values;
    int nextParam = currentParam + 1;
    while (theValue != 0) {
      char *paramValue = theValue->value;
      paramValues[currentParam] = paramValue;
      EvalFileWithParameters(interp, tclStartupFileScript, theNextParam,
                             nextParam, rank, np);

      theValue = theValue->next;
    }
  } else {

    simulationInfo.start();
    static int count = 0;

    if ((count % np) == rank) {
      Tcl_Eval(interp, "wipe");

      for (int i = 0; i < numParam; i++) {

        Tcl_SetVar(interp, paramNames[i], paramValues[i], TCL_GLOBAL_ONLY);

        simulationInfo.addParameter(paramNames[i], paramValues[i]);
      }

      count++;

      const char *pwd = getInterpPWD(interp);
      simulationInfo.addInputFile(tclStartupFileScript, pwd);

      int ok = Tcl_EvalFile(interp, tclStartupFileScript);

      simulationInfo.end();

      return ok;
    } else
      count++;
  }

  return 0;
}


int
maxOpenFiles(ClientData clientData, Tcl_Interp *interp, int argc,
             TCL_Char **argv)
{
  int maxOpenFiles;

  if (Tcl_GetInt(interp, argv[1], &maxOpenFiles) != TCL_OK) {
    return TCL_ERROR;
  }

#ifdef _WIN32
  int newMax = _setmaxstdio(maxOpenFiles);
  if (maxOpenFiles > 2048) {
    opserr << "setMaxOpenFiles: too many files specified (2048 max)\n";
  } else {
    if (newMax != maxOpenFiles) {
      opserr << "setMaxOpenFiles FAILED: max allowed files: " << newMax;
      return TCL_ERROR;
    }
  }
  return TCL_OK;
#endif

  opserr << "setMaxOpenFiles FAILED: - command not available on this machine\n";
  return TCL_OK;
}

