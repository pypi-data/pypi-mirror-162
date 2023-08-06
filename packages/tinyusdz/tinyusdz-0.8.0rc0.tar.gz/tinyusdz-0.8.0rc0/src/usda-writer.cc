// SPDX-License-Identifier: MIT
// Copyright 2022 - Present, Syoyo Fujita.
//
// USDA(Ascii) writer
//

#include "usda-writer.hh"

#if !defined(TINYUSDZ_DISABLE_MODULE_USDA_WRITER)

#include <fstream>
#include <iostream>
#include <sstream>

#include "pprinter.hh"
#include "value-pprint.hh"

namespace tinyusdz {
namespace usda {

namespace {

inline std::string GetTypeName(XformOpValueType const &v) {
  return value::GetTypeName(v.id());
}

class Writer {
 public:
  Writer(const Stage &stage) : _stage(stage) {}

  std::string Indent(size_t level) {
    std::stringstream ss;
    for (size_t i = 0; i < level; i++) {
      ss << "  ";
    }

    return ss.str();
  }

  bool WriteGeomMesh(std::ostream &ofs, const GeomMesh &mesh, uint32_t level) {

    ofs << to_string(mesh, level, /* closing brace */false);

    ofs << Indent(level) << "}\n";

    return true;
  }

  bool WriteXform(std::ostream &ofs, const Xform &xform, uint32_t level) {
    std::cout << "Writing Xform: " << xform.name << " ...\n";

    ofs << Indent(level) << "\n";
    ofs << Indent(level) << "def Xform \"" << xform.name << "\"\n";
    ofs << Indent(level) << "{\n";

    if (xform.xformOps.size()) {
      // xformOpOrder
      ofs << Indent(level + 1) << "uniform token[] xformOpOrder = [";

      for (size_t i = 0; i < xform.xformOps.size(); i++) {
        ofs << "\"" << XformOp::GetOpTypeName(xform.xformOps[i].op) << "\"";

        if (i != (xform.xformOps.size() - 1)) {
          ofs << ", ";
        }
      }

      ofs << "]\n";

      for (size_t i = 0; i < xform.xformOps.size(); i++) {
        ofs << Indent(level + 1);

        ofs << GetTypeName(xform.xformOps[i].value);

        ofs << " " << XformOp::GetOpTypeName(xform.xformOps[i].op) << " = ";

#if 0 // TODO
        nonstd::visit([&ofs](XformOpValueType &&arg) { ofs << arg; },
                      xform.xformOps[i].value);
#endif
        ofs << "\n";
      }
    }

    return true;
  }

#if 0
  bool WriteNode(std::ostream &ofs, const Node &node, uint32_t level) {
    if (node.type == NODE_TYPE_XFORM) {
      if ((node.index < 0) || (size_t(node.index) >= _stage.xforms.size())) {
        // invalid index
        return false;
      }

      if (!WriteXform(ofs, _stage.xforms.at(size_t(node.index)), level)) {
        return false;
      }

    } else if (node.type == NODE_TYPE_GEOM_MESH) {
      if ((node.index < 0) ||
          (size_t(node.index) >= _stage.geom_meshes.size())) {
        // invalid index
        return false;
      }

      if (!WriteGeomMesh(ofs, _stage.geom_meshes.at(size_t(node.index)),
                         level)) {
        return false;
      }

    } else {
      // unimplemented/unsupported node.
      _err += "TODO: Unimplemnted node type.\n";
      return false;
    }

    for (const auto &child : node.children) {
      if (!WriteNode(ofs, child, level + 1)) {
        return false;
      }
    }

    ofs << Indent(level) << "}\n";

    return true;
  }
#endif

  const Stage &_stage;

  const std::string &Error() const { return _err; }
  const std::string &Warn() const { return _warn; }

 private:
  Writer() = delete;
  Writer(const Writer &) = delete;

  std::string _err;
  std::string _warn;
};

}  // namespace

bool SaveAsUSDA(const std::string &filename, const Stage &stage,
                std::string *warn, std::string *err) {

  (void)warn;

  std::stringstream ss;

  ss << "#usda 1.0\n";
  ss << "(\n";
  if (stage.stage_metas.doc.empty()) {
    ss << "  doc = \"TinyUSDZ v" << tinyusdz::version_major << "."
       << tinyusdz::version_minor << "." << tinyusdz::version_micro << "\"\n";
  } else {
    ss << "  doc = \"" << stage.stage_metas.doc << "\"\n";
  }
  ss << "  metersPerUnit = " << stage.stage_metas.metersPerUnit << "\n";
  ss << "  upAxis = \"" << to_string(stage.stage_metas.upAxis) << "\"\n";
  ss << "  timeCodesPerSecond = \"" << stage.stage_metas.timeCodesPerSecond << "\"\n";
  // TODO: write other header data.
  ss << ")\n";

  // TODO
  Writer writer(stage);

#if 0 // TODO
  std::cout << "# of nodes: " << stage.nodes.size() << "\n";

  for (const auto &root : stage.nodes) {
    if (!writer.WriteNode(ss, root, 0)) {
      if (err && writer.Error().size()) {
        (*err) += writer.Error();
      }

      if (warn && writer.Warn().size()) {
        (*warn) += writer.Warn();
      }

      return false;
    }
  }
#endif

  std::ofstream ofs(filename);
  if (!ofs) {
    if (err) {
      (*err) += "Failed to open file [" + filename + "] to write.\n";
    }
    return false;
  }

  ofs << ss.str();

  std::cout << "Wrote to [" << filename << "]\n";

  return true;
}

} // namespace usda
}  // namespace tinyusdz

#else

namespace tinyusdz {
namespace usda {

bool SaveAsUSDA(const std::string &filename, const Stage &stage, std::string *warn, std::string *err) {
  (void)filename;
  (void)stage;
  (void)warn;

  if (err) {
    (*err) = "USDA Writer feature is disabled in this build.\n";
  }
  return false;
}



} // namespace usda
}  // namespace tinyusdz
#endif


