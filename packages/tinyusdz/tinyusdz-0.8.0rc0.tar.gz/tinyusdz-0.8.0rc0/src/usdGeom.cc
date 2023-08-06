// SPDX-License-Identifier: MIT
// Copyright 2022 - Present, Syoyo Fujita.
//
// UsdGeom API implementations

#include <sstream>

#include "usdGeom.hh"
#include "prim-types.hh"

#include "common-macros.inc"

namespace tinyusdz {

namespace {

constexpr auto kPrimvarNormals = "primvar::normals";

} // namespace

std::vector<value::normal3f> GeomMesh::GetNormals() const {
  std::vector<value::normal3f> dst;

  if (props.count(kPrimvarNormals)) {
    const auto prop = props.at(kPrimvarNormals);
    if (prop.IsRel()) {
      // TODO:
      return dst;
    }

    if (prop.attrib.var.type_name() == "normal3f[]") {
      if (auto pv = prop.attrib.var.get_value<std::vector<value::normal3f>>()) {
        dst = pv.value();
      }
    }
  } else if (normals) {
    if (normals.value().var.type_name() == "normal3f[]") {
      if (auto pv = normals.value().var.get_value<std::vector<value::normal3f>>()) {
        dst = pv.value();
      }
    }
  }

  return dst;
}

Interpolation GeomMesh::GetNormalsInterpolation() const {

  if (props.count(kPrimvarNormals)) {
    // TODO: Check if `primvar::normals` type is `normal3f[]`
    const auto &prop = props.at(kPrimvarNormals);
    if (prop.attrib.meta.interpolation) {
      return prop.attrib.meta.interpolation.value();
    }
  } else if (normals) {
    return normals.value().meta.interpolation.value();
  }

  return Interpolation::Vertex; // default 'vertex'
}

void GeomMesh::Initialize(const GPrim &gprim)
{
  name = gprim.name;
  parent_id = gprim.parent_id;

  props = gprim.props;

#if 0
  for (auto &prop_item : gprim.props) {
    std::string attr_name = std::get<0>(prop_item);
    const Property &prop = std::get<1>(prop_item);

    if (prop.is_rel) {
      //LOG_INFO("TODO: Rel property:" + attr_name);
      continue;
    }

    const PrimAttrib &attr = prop.attrib;

    if (attr_name == "points") {
      //if (auto p = primvar::as_vector<value::float3>(&attr.var)) {
      //  points = *p;
      //}
    } else if (attr_name == "faceVertexIndices") {
      //if (auto p = primvar::as_vector<int>(&attr.var)) {
      //  faceVertexIndices = *p;
      //}
    } else if (attr_name == "faceVertexCounts") {
      //if (auto p = primvar::as_vector<int>(&attr.var)) {
      //  faceVertexCounts = *p;
      //}
    } else if (attr_name == "normals") {
      //if (auto p = primvar::as_vector<value::float3>(&attr.var)) {
      //  normals.var = *p;
      //  normals.interpolation = attr.interpolation;
      //}
    } else if (attr_name == "velocitiess") {
      //if (auto p = primvar::as_vector<value::float3>(&attr.var)) {
      //  velocitiess.var = (*p);
      //  velocitiess.interpolation = attr.interpolation;
      //}
    } else if (attr_name == "primvars:uv") {
      //if (auto pv2f = primvar::as_vector<Vec2f>(&attr.var)) {
      //  st.buffer = (*pv2f);
      //  st.interpolation = attr.interpolation;
      //} else if (auto pv3f = primvar::as_vector<value::float3>(&attr.var)) {
      //  st.buffer = (*pv3f);
      //  st.interpolation = attr.interpolation;
      //}
    } else {
      // Generic PrimAtrr
      props[attr_name] = attr;
    }

  }
#endif

  doubleSided = gprim.doubleSided;
  orientation = gprim.orientation;
  visibility = gprim.visibility;
  extent = gprim.extent;
  purpose = gprim.purpose;

  displayColor = gprim.displayColor;
  displayOpacity = gprim.displayOpacity;

#if 0 // TODO


  // PrimVar(TODO: Remove)
  UVCoords st;

  //
  // Properties
  //


#endif

};

nonstd::expected<bool, std::string> GeomMesh::ValidateGeomSubset() {

  std::stringstream ss;

  if (geom_subset_children.empty()) {
    return true;
  }

  auto CheckFaceIds = [](const size_t nfaces, const std::vector<uint32_t> ids) {
    if (std::any_of(ids.begin(), ids.end(), [&nfaces](uint32_t id) { return id >= nfaces; })) {
      return false;
    }

    return true;
  };

  size_t n = faceVertexIndices.size();

  // Currently we only check if face ids are valid.
  for (size_t i = 0; i < geom_subset_children.size(); i++) {
    const GeomSubset & subset = geom_subset_children[i];

    if (!CheckFaceIds(n, subset.indices)) {
      ss << "Face index out-of-range.\n";
      return nonstd::make_unexpected(ss.str());
    }
  }

  return nonstd::make_unexpected("TODO: Implent GeomMesh::ValidateGeomSubset\n");
  //return true;

}

namespace {

#if 0
value::matrix4d GetTransform(XformOp xform)
{
  value::matrix4d m;
  Identity(&m);

  if (xform.op == XformOp::OpType::TRANSFORM) {
    if (auto v = xform.value.get<value::matrix4d>()) {
      m = v.value();
    }
  } else if (xform.op == XformOp::OpType::TRANSLATE) {
      if (auto sf = xform.value.get<value::float3>()) {
        m.m[3][0] = double(sf.value()[0]);
        m.m[3][1] = double(sf.value()[1]);
        m.m[3][2] = double(sf.value()[2]);
      } else if (auto sd = xform.value.get<value::double3>()) {
        m.m[3][0] = sd.value()[0];
        m.m[3][1] = sd.value()[1];
        m.m[3][2] = sd.value()[2];
      }
  } else if (xform.op == XformOp::OpType::SCALE) {
      if (auto sf = xform.value.get<value::float3>()) {
        m.m[0][0] = double(sf.value()[0]);
        m.m[1][1] = double(sf.value()[1]);
        m.m[2][2] = double(sf.value()[2]);
      } else if (auto sd = xform.value.get<value::double3>()) {
        m.m[0][0] = sd.value()[0];
        m.m[1][1] = sd.value()[1];
        m.m[2][2] = sd.value()[2];
      }
  } else {
    DCOUT("TODO: xform.op = " << XformOp::GetOpTypeName(xform.op));
  }

  return m;
}
#endif

} // namespace

bool Xform::EvaluateXformOps(value::matrix4d *out_matrix) const {
    Identity(out_matrix);

    value::matrix4d cm;

    // Concat matrices
    for (const auto &x : xformOps) {
      value::matrix4d m;
      Identity(&m);
      (void)x;
      if (x.op == XformOp::TRANSLATE) {
        if (auto txf = x.value.get<value::float3>()) {
          m.m[3][0] = double(txf.value()[0]);
          m.m[3][1] = double(txf.value()[1]);
          m.m[3][2] = double(txf.value()[2]);
        } else if (auto txd = x.value.get<value::double3>()) {
          m.m[3][0] = txd.value()[0];
          m.m[3][1] = txd.value()[1];
          m.m[3][2] = txd.value()[2];
        } else {
          return false;
        }
      // FIXME: Validate ROTATE_X, _Y, _Z implementation
      } else if (x.op == XformOp::ROTATE_X) {
        double theta;
        if (auto rf = x.value.get<float>()) {
          theta = double(rf.value());
        } else if (auto rd = x.value.get<double>()) {
          theta = rd.value();
        } else {
          return false;
        }

        m.m[1][1] = std::cos(theta);
        m.m[1][2] = std::sin(theta);
        m.m[2][1] = -std::sin(theta);
        m.m[2][2] = std::cos(theta);
      } else if (x.op == XformOp::ROTATE_Y) {
        double theta;
        if (auto f = x.value.get<float>()) {
          theta = double(f.value());
        } else if (auto d = x.value.get<double>()) {
          theta = d.value();
        } else {
          return false;
        }

        m.m[0][0] = std::cos(theta);
        m.m[0][2] = -std::sin(theta);
        m.m[2][0] = std::sin(theta);
        m.m[2][2] = std::cos(theta);
      } else if (x.op == XformOp::ROTATE_Z) {
        double theta;
        if (auto f = x.value.get<float>()) {
          theta = double(f.value());
        } else if (auto d = x.value.get<double>()) {
          theta = d.value();
        } else {
          return false;
        }

        m.m[0][0] = std::cos(theta);
        m.m[0][1] = std::sin(theta);
        m.m[1][0] = -std::sin(theta);
        m.m[1][1] = std::cos(theta);
      } else {
        // TODO
        DCOUT("TODO");
        return false;
      }

      cm = Mult<value::matrix4d, double, 4>(cm, m);
    }

    (*out_matrix) = cm;

  return true;
}

} // namespace tinyusdz


