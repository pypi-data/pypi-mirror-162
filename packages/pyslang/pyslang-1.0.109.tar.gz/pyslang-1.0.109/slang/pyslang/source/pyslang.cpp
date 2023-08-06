//------------------------------------------------------------------------------
// pyslang.cpp
// File is under the MIT license; see LICENSE for details
//------------------------------------------------------------------------------
#include "pyslang.h"

void registerCompilation(py::module_& m);
void registerNumeric(py::module_& m);
void registerUtil(py::module_& m);
void registerSyntax(py::module_& m);
void registerSyntaxNodes(py::module_& m);

PYBIND11_MODULE(pyslang, m) {
    m.doc() = "Python bindings for slang, the SystemVerilog compiler library";

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif

    registerCompilation(m);
    registerNumeric(m);
    registerUtil(m);
    registerSyntax(m);
    registerSyntaxNodes(m);
}
