#include "render-data.hh"

#include "pprinter.hh"
#include "prim-types.hh"

namespace tinyusdz {
namespace tydra {

namespace {

#if 0
template <typename T>
inline T Get(const nonstd::optional<T> &nv, const T &default_value) {
  if (nv) {
    return nv.value();
  }
  return default_value;
}
#endif

}  // namespace

nonstd::expected<RenderMesh, std::string> Convert(const Stage &stage, const GeomMesh &mesh) {
  RenderMesh dst;

  {
    dst.points.resize(mesh.points.size());
    memcpy(dst.points.data(), mesh.points.data(),
           sizeof(value::float3) * mesh.points.size());
  }

  // normals
  {
    std::vector<value::normal3f> normals = mesh.GetNormals();
    Interpolation interp = mesh.GetNormalsInterpolation();

    if (interp == Interpolation::Vertex) {
      return nonstd::make_unexpected(
          "TODO: `vertex` interpolation for `normals` attribute.\n");
    } else if (interp == Interpolation::FaceVarying) {
      dst.facevaryingNormals.resize(normals.size());
      memcpy(dst.facevaryingNormals.data(), normals.data(),
             sizeof(value::normal3f) * normals.size());
    } else {
      return nonstd::make_unexpected(
          "Unsupported/unimplemented interpolation for `normals` attribute: " +
          to_string(interp) + ".\n");
    }
  }

  // uvs
  // Procedure:
  // - Find Shader
  // - Lookup PrimvarReader
  (void)stage;

  return std::move(dst);
}

}  // namespace tydra
}  // namespace tinyusdz
