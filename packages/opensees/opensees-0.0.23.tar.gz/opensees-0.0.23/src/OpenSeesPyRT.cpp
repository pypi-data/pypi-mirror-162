#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <G3_Runtime.h>
#include <elementAPI.h> // G3_getRuntime/SafeBuilder
#include "TclSafeBuilder.h"

#include <Domain.h>
#include <Vector.h>
#include <Node.h>
#include <Element.h>
#include <SectionForceDeformation.h>
#include <UniaxialMaterial.h>
#include <HystereticBackbone.h>

#include <ManderBackbone.h>


// 
// ANALYSIS
//
// #include <AnalysisRuntime.h>
#include <TransientAnalysis.h>
#include <DirectIntegrationAnalysis.h>
#include <StaticAnalysis.h>

#include <LoadPattern.h>
#include <EarthquakePattern.h>
#include <GroundMotion.h>
#include <UniformExcitation.h>
#include <TimeSeries.h>
#include <PathTimeSeries.h>
#include <PathSeries.h>
#include <LinearSeries.h>
#include <GroundMotion.h>
#define ARRAY_FLAGS py::array::c_style|py::array::forcecast
/*
GroundMotion*
quake2sees_motion(
    pybind11::array_t<double,pybind11::array::c_style|pybind11::array::forcecast>, 
    double time_step,
    double time_start = 0.0,
    double cfactor = 1.0,
    int tag = 0
);
*/



std::unique_ptr<G3_Runtime, py::nodelete> 
getRuntime(py::object interpaddr) {
      void *interp_addr;
      interp_addr = (void*)PyLong_AsVoidPtr(interpaddr.ptr());
      return std::unique_ptr<G3_Runtime, py::nodelete>(G3_getRuntime((Tcl_Interp*)interp_addr));
} // , py::return_value_policy::reference

std::unique_ptr<TclSafeBuilder, py::nodelete> 
get_builder(py::object interpaddr) {
      void *interp_addr;
      interp_addr = (void*)PyLong_AsVoidPtr(interpaddr.ptr());
      void *builder_addr = G3_getSafeBuilder(G3_getRuntime((Tcl_Interp*)interp_addr));
      return std::unique_ptr<TclSafeBuilder, py::nodelete>((TclSafeBuilder*)builder_addr);
} // , py::return_value_policy::reference


class PyHystereticBackbone : public HystereticBackbone {
public:
    /* Inherit the constructors */
    using HystereticBackbone::HystereticBackbone;

    /* Trampoline (need one for each virtual function) */
    double getStress(double strain) override {
        PYBIND11_OVERRIDE_PURE(
            double,                 /* Return type */
            HystereticBackbone,     /* Parent class */
            getStress,              /* Name of function in C++ (must match Python name) */
            strain                  /* Argument(s) */
        );
    }
};

py::array_t<double>
copy_vector(Vector vector)
{
  py::array_t<double> array(vector.Size());
  double *ptr = static_cast<double*>(array.request().ptr);
  for (int i=0; i<vector.Size(); i++)
    ptr[i] = vector(i);
  return array;
}

Vector *
new_vector(py::array_t<double> array)
{
  py::buffer_info info = array.request();
  return new Vector(static_cast<double*>(info.ptr),(int)info.shape[0]);
}

py::array_t<double>
copy_matrix(Matrix matrix)
{
  int nr = matrix.noRows();
  int nc = matrix.noCols();
  py::array_t<double> array({nr,nc},{nr*nc*sizeof(double), nc*sizeof(double)});
  double *ptr = static_cast<double*>(array.request().ptr);

  for (int i=0; i<matrix.noRows(); i++)
    for (int j=0; j<matrix.noCols(); j++)
      ptr[i*nc+j] = matrix(i,j);
  return array;
}


GroundMotion*
quake2sees_motion(
    py::array_t<double,ARRAY_FLAGS> quake_array, 
    double time_step, 
    double time_start = 0.0, 
    double cfactor = 1.0,
    int tag = 110
)
{
    Vector *accel;
    TimeSeries *accelSeries;
    GroundMotion *groundMotion;
    /* quake -> {Vector} */
    py::buffer_info info = quake_array.request();
    double* accel_array = static_cast<double*>(info.ptr);
    int array_size = static_cast<int>(info.shape[0]);
    accel = new Vector(accel_array,array_size);

    /* {Vector} -> {TimeSeries:PathTimeSeries} */
    accelSeries = new PathSeries(tag, *accel, time_step, cfactor, false, time_start);

    groundMotion = new GroundMotion(0, 0, accelSeries, 0);
    return groundMotion;
    /* TimeSeries -> Pattern:UniformExcitation */

}

GroundMotion*
ground_motion(
    double* accel_array, 
    int array_size,
    double time_step, 
    double time_start = 0.0, 
    double cfactor = 1.0,
    int tag = 110
)
{
    Vector *accel;
    TimeSeries *accelSeries;
    GroundMotion *groundMotion;
    /* quake -> {Vector} */
    accel = new Vector(accel_array,array_size);

    /* {Vector} -> {TimeSeries:PathTimeSeries} */
    accelSeries = new PathSeries(tag, *accel, time_step, cfactor, false, time_start);

    groundMotion = new GroundMotion(0, 0, accelSeries, 0);
    return groundMotion;
    /* TimeSeries -> Pattern:UniformExcitation */

}

void
init_obj_module(py::module &m)
{
  py::class_<Vector, std::unique_ptr<Vector, py::nodelete>> PyVector(m, "Vector", py::buffer_protocol());
  PyVector.def (py::init([](
        py::array_t<double, py::array::c_style|py::array::forcecast> array
      ) -> Vector {
        bool verbose = false;
        py::buffer_info info = array.request();
        if (verbose){
          py::print("ptr\t", info.ptr);
          py::print("itemsize\t", info.itemsize);
          py::print("format\t", info.format);
          py::print("ndim\t", info.ndim);
          py::print("shape\t", py::cast(info.shape));
          py::print("strides\t", py::cast(info.strides));
          py::print("array\t", array);
          printf("%lf\n", *((double*)info.ptr));
        }
        return Vector(static_cast<double*>(info.ptr),(int)info.shape[0]);
      }))
      /* Allow reference by numpy array; requires access to Vector.theData */
      // .def_buffer([](Vector& v) -> py::buffer_info{
      //       return py::buffer_info(
      //       );
      // })

      /* pyg3.Vector(array:Seq, assert_size:int) */
      .def (py::init([](
        py::array_t<double, py::array::c_style|py::array::forcecast> array,
        int assert_size
      ) -> Vector {
        bool verbose = true;
        py::buffer_info info = array.request();
        if (verbose){
          py::print("ptr\t",info.ptr);
          py::print("itemsize\t", info.itemsize);
          py::print("format\t", info.format);
          py::print("ndim\t", info.ndim);
          py::print("shape\t", py::cast(info.shape));
          py::print("strides\t", py::cast(info.strides));
        }
        if (info.shape[0] != assert_size)
          throw std::runtime_error("Incompatible buffer dimension.");
        return Vector(static_cast<double*>(info.ptr), static_cast<int>(info.shape[0]));
      }))
  ;
  py::class_<Matrix, std::unique_ptr<Matrix, py::nodelete>>(m, "Matrix", py::buffer_protocol())
      .def (py::init([](
          py::array_t<double, py::array::c_style|py::array::forcecast> array,
          int assert_size
      ) -> Matrix {
        bool verbose = true;
        py::buffer_info info = array.request();
        if (verbose){
          py::print("ptr\t",info.ptr);
          py::print("itemsize\t", info.itemsize);
          py::print("format\t", info.format);
          py::print("ndim\t", info.ndim);
          py::print("shape\t", py::cast(info.shape));
          py::print("strides\t", py::cast(info.strides));
        }
        if (info.shape[0] != assert_size)
          throw std::runtime_error("Incompatible buffer dimension.");
        return Matrix(
          static_cast<double*>(info.ptr), 
          static_cast<int>(info.shape[0]),
          static_cast<int>(info.shape[1])
        );
      }))
  ; 
  py::class_<Node,    std::unique_ptr<Node,py::nodelete>>(m, "_Node")
  ;
  py::class_<Element, std::unique_ptr<Element,py::nodelete>>(m, "_Element")
    .def ("commitState",           &Element::commitState)
    .def ("revertToStart",         &Element::revertToStart)
    .def ("revertToLastCommit",    &Element::revertToLastCommit)
  ;

  py::class_<SectionForceDeformation, std::unique_ptr<SectionForceDeformation, py::nodelete> > (m, "_SectionForceDeformation")
    .def ("getSectionTangent",          [](SectionForceDeformation& section) {
      return copy_matrix(section.getSectionTangent());
    })
    .def ("getInitialTangent",          [](SectionForceDeformation& section) {
      return copy_matrix(section.getInitialTangent());
    })
    .def ("getSectionFlexibility",      [](SectionForceDeformation& section) {
      return copy_matrix(section.getSectionFlexibility());
    })
    .def ("getInitialFlexibility",      [](SectionForceDeformation& section) {
      return copy_matrix(section.getInitialFlexibility());
    })
    .def ("setTrialSectionDeformation", [](SectionForceDeformation& section,  
        py::array_t<double, py::array::c_style|py::array::forcecast> deformation) {
      return section.setTrialSectionDeformation(*new_vector(deformation));
    }) 
    .def ("setTrialSectionDeformation", [](SectionForceDeformation& section, Vector &deformation) {
      return section.setTrialSectionDeformation(deformation);
    }) 
    .def ("getSectionDeformation", &SectionForceDeformation::getSectionDeformation)

    .def ("getStressResultant",    [](SectionForceDeformation &section, py::array_t<double> deformation, bool commit=false) {
      section.setTrialSectionDeformation(*new_vector(deformation));
      if (commit) section.commitState();
      return copy_vector(section.getStressResultant());
    })
    .def ("getStressResultant",    [](SectionForceDeformation &section) {
        return copy_vector(section.getStressResultant());
    })
    .def ("commitState",           &SectionForceDeformation::commitState)
    .def ("revertToStart",         &SectionForceDeformation::revertToStart)
    .def ("revertToLastCommit",    &SectionForceDeformation::revertToLastCommit)
  ;

  py::class_<UniaxialMaterial, std::unique_ptr<UniaxialMaterial, py::nodelete>>(m, "_UniaxialMaterial")
    .def ("setTrialStrain",        [](UniaxialMaterial &material, double strain) {
        return material.setTrialStrain(strain);
      }
    )
    .def ("getStress",             &UniaxialMaterial::getStress)
    .def ("getStress",            [](UniaxialMaterial &material, double strain, bool commit=false){
        material.setTrialStrain(strain);
        if (commit)  material.commitState();
        return material.getStress();
    }, py::arg("strain"), py::arg("commit"))
    .def ("getTangent",            &UniaxialMaterial::getTangent)
    .def ("getDampTangent",        &UniaxialMaterial::getDampTangent)
    .def ("getStrainRate",         &UniaxialMaterial::getStrainRate)
    .def ("commitState",           &UniaxialMaterial::commitState)
    .def ("revertToStart",         &UniaxialMaterial::revertToStart)
    .def ("revertToLastCommit",    &UniaxialMaterial::revertToLastCommit)
  ;

  py::class_<HystereticBackbone, PyHystereticBackbone>(m, "HystereticBackbone")
    .def("getStress", &HystereticBackbone::getStress);
  ;

  py::class_<ManderBackbone, HystereticBackbone>(m, "PopovicsBackbone")
    .def(py::init<int, double, double, double>(),
         py::arg("tag"), py::arg("f"), py::arg("e"), py::arg("E")
    )
    .def("getStress", &ManderBackbone::getStress)
  ;




    py::class_<TimeSeries, std::unique_ptr<TimeSeries, py::nodelete> >(m, "TimeSeries");
    py::class_<PathTimeSeries>(m, "PathTimeSeries");
    py::class_<LinearSeries, TimeSeries, std::unique_ptr<LinearSeries, py::nodelete> >(m, "LinearSeries")
        .def (py::init())
        .def ("getFactor",     &LinearSeries::getFactor)
    ;
    py::class_<LoadPattern, std::unique_ptr<LoadPattern, py::nodelete> >(m, "LoadPattern",
         "The `LoadPattern` class is a concrete base class. A `LoadPattern "
         "is a container class for `Load` and `SP_Constraint objects."
         )
        .def (py::init<int>())
        .def ("setTimeSeries", &LoadPattern::setTimeSeries)
    ;
    py::class_<EarthquakePattern, LoadPattern>(m, "EarthquakePattern");

    py::class_<UniformExcitation, EarthquakePattern>(m, "UniformExcitation")
        .def (py::init< \
                GroundMotion&,
                int,
                int,
                double,
                double>(),
              py::arg("motion"),
              py::arg("dof"),
              py::arg("tag"),
              py::arg("vel") = 0.0,
              py::arg("factor") = 1.0
        )
        .def (py::init([](
             int tag,
             int dof,
             py::array_t<double,py::array::c_style|py::array::forcecast> motion,
             double time_step,
             double vel=0.0,
             double factor=1.0
        ) -> UniformExcitation {
             printf("called\n\n\n");
             GroundMotion *ground_motion = quake2sees_motion(motion, time_step);
             return UniformExcitation(*ground_motion, dof, tag, vel, factor);
        }), 
             py::arg("tag"), py::arg("dof"), py::arg("accel"), py::arg("time_step"),
             py::arg("init_veloc")=0.0, py::arg("factor")=1.0
        )
    ;

  py::class_<TclSafeBuilder, std::unique_ptr<TclSafeBuilder, py::nodelete> >(m, "TclTclSafeBuilder")
    .def (py::init([](py::object interpaddr)->std::unique_ptr<TclSafeBuilder, py::nodelete>{
        void *interp_addr;
        interp_addr = (void*)PyLong_AsVoidPtr(interpaddr.ptr());
        void *builder_addr = Tcl_GetAssocData((Tcl_Interp*)interp_addr, "OPS::theTclSafeBuilder", NULL);
        return std::unique_ptr<TclSafeBuilder, py::nodelete>((TclSafeBuilder*)builder_addr);
      }) // , py::return_value_policy::reference
    )
    .def ("getSection", [](TclSafeBuilder& builder, py::str id){
        return builder.getSection(id);
    })
    .def ("getUniaxialMaterial", [](TclSafeBuilder& builder, py::str tag){
        return builder.getUniaxialMaterial(tag);
    })
    .def ("getUniaxialMaterial", [](TclSafeBuilder& builder, int tag){
        return builder.getUniaxialMaterial(tag);
    })
    .def ("getHystereticBackbone", [](TclSafeBuilder& builder, std::string tag){
        return std::unique_ptr<HystereticBackbone, py::nodelete>(builder.getHystereticBackbone(tag));
    })
  ;

  py::class_<Domain>(m, "_Domain")
    .def ("getNodeResponse", [](Domain&domain, int node, std::string type) {
        NodeResponseType typ;
        if (type == "displ") typ = Disp;
        if (type == "accel") typ = Accel;
        if (type == "veloc") typ = Vel;
        if (type == "react") typ = Reaction;
      return copy_vector(*domain.getNodeResponse(node, typ));
    })
  ;
  
  py::class_<G3_Runtime>(m, "_Runtime")
  ;

  py::class_<StaticAnalysis>(m, "_StaticAnalysis")
    .def (py::init([](G3_Runtime *runtime, G3_Config  conf) {
      return *((StaticAnalysis*)runtime->newStaticAnalysis(conf));
    }))
    .def ("analyze", &StaticAnalysis::analyze)
  ;

  py::class_<TransientAnalysis>(m, "TransientAnalysis");
  // py::class_<TransientAnalysis>(m, "_TransientAnalysis") // , std::unique_ptr<TransientAnalysis, py::nodelete>>(m, "_TransientAnalysis")
  py::class_<DirectIntegrationAnalysis, TransientAnalysis>(m, "_DirectIntegrationAnalysis")
    .def (py::init([](G3_Runtime *runtime, G3_Config  conf) {
      return *((DirectIntegrationAnalysis*)runtime->newTransientAnalysis(conf));
    }))
    .def ("analyze", &TransientAnalysis::analyze)
  ;

  m.def ("get_builder", &get_builder);
  m.def ("getRuntime",  &getRuntime);
  m.def ("get_domain", [](G3_Runtime *rt)->std::unique_ptr<Domain, py::nodelete>{
      Domain *domain_addr = rt->m_domain;
      return std::unique_ptr<Domain, py::nodelete>((Domain*)domain_addr);
    } // , py::return_value_policy::reference
  );

}

PYBIND11_MODULE(libOpenSeesRT, m) {init_obj_module(m);}

