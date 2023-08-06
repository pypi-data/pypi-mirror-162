// SPDX-License-Identifier: MIT
#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include "value-types.hh"

#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"
#endif

#include "nonstd/expected.hpp"
#include "nonstd/optional.hpp"
#include "external/better-enums/enum.h"

#ifdef __clang__
#pragma clang diagnostic pop
#endif

#include "primvar.hh"
#include "tiny-variant.hh"

namespace tinyusdz {

template <typename T>
class ListOp {
 public:
  ListOp() : is_explicit(false) {}

  void ClearAndMakeExplicit() {
    explicit_items.clear();
    added_items.clear();
    prepended_items.clear();
    appended_items.clear();
    deleted_items.clear();
    ordered_items.clear();

    is_explicit = true;
  }

  bool IsExplicit() const { return is_explicit; }
  bool HasExplicitItems() const { return explicit_items.size(); }

  bool HasAddedItems() const { return added_items.size(); }

  bool HasPrependedItems() const { return prepended_items.size(); }

  bool HasAppendedItems() const { return appended_items.size(); }

  bool HasDeletedItems() const { return deleted_items.size(); }

  bool HasOrderedItems() const { return ordered_items.size(); }

  const std::vector<T> &GetExplicitItems() const { return explicit_items; }

  const std::vector<T> &GetAddedItems() const { return added_items; }

  const std::vector<T> &GetPrependedItems() const { return prepended_items; }

  const std::vector<T> &GetAppendedItems() const { return appended_items; }

  const std::vector<T> &GetDeletedItems() const { return deleted_items; }

  const std::vector<T> &GetOrderedItems() const { return ordered_items; }

  void SetExplicitItems(const std::vector<T> &v) { explicit_items = v; }

  void SetAddedItems(const std::vector<T> &v) { added_items = v; }

  void SetPrependedItems(const std::vector<T> &v) { prepended_items = v; }

  void SetAppendedItems(const std::vector<T> &v) { appended_items = v; }

  void SetDeletedItems(const std::vector<T> &v) { deleted_items = v; }

  void SetOrderedItems(const std::vector<T> &v) { ordered_items = v; }

 private:
  bool is_explicit{false};
  std::vector<T> explicit_items;
  std::vector<T> added_items;
  std::vector<T> prepended_items;
  std::vector<T> appended_items;
  std::vector<T> deleted_items;
  std::vector<T> ordered_items;
};

struct ListOpHeader {
  enum Bits {
    IsExplicitBit = 1 << 0,
    HasExplicitItemsBit = 1 << 1,
    HasAddedItemsBit = 1 << 2,
    HasDeletedItemsBit = 1 << 3,
    HasOrderedItemsBit = 1 << 4,
    HasPrependedItemsBit = 1 << 5,
    HasAppendedItemsBit = 1 << 6
  };

  ListOpHeader() : bits(0) {}

  explicit ListOpHeader(uint8_t b) : bits(b) {}

  explicit ListOpHeader(ListOpHeader const &op) : bits(0) {
    bits |= op.IsExplicit() ? IsExplicitBit : 0;
    bits |= op.HasExplicitItems() ? HasExplicitItemsBit : 0;
    bits |= op.HasAddedItems() ? HasAddedItemsBit : 0;
    bits |= op.HasPrependedItems() ? HasPrependedItemsBit : 0;
    bits |= op.HasAppendedItems() ? HasAppendedItemsBit : 0;
    bits |= op.HasDeletedItems() ? HasDeletedItemsBit : 0;
    bits |= op.HasOrderedItems() ? HasOrderedItemsBit : 0;
  }

  bool IsExplicit() const { return bits & IsExplicitBit; }

  bool HasExplicitItems() const { return bits & HasExplicitItemsBit; }
  bool HasAddedItems() const { return bits & HasAddedItemsBit; }
  bool HasPrependedItems() const { return bits & HasPrependedItemsBit; }
  bool HasAppendedItems() const { return bits & HasAppendedItemsBit; }
  bool HasDeletedItems() const { return bits & HasDeletedItemsBit; }
  bool HasOrderedItems() const { return bits & HasOrderedItemsBit; }

  uint8_t bits;
};

enum class SpecType {
  Attribute,
  Connection,
  Expression,
  Mapper,
  MapperArg,
  Prim,
  PseudoRoot,
  Relationship,
  RelationshipTarget,
  Variant,
  VariantSet,
  Invalid,
};

enum class Orientation {
  RightHanded,  // 0
  LeftHanded,
  Invalid
};

enum class Visibility {
  Inherited,  // 0
  Invisible,
  Invalid
};

enum class Purpose {
  Default,  // 0
  Render,
  Proxy,
  Guide,
  Invalid
};

enum class SubdivisionScheme {
  CatmullClark,  // 0
  Loop,
  Bilinear,
  None,
  Invalid
};

enum class Kind {
  Model,
  Group,
  Assembly,
  Component,
  Subcomponent,
  Invalid
};

// Attribute interpolation
enum class Interpolation {
  Constant,     // "constant"
  Uniform,      // "uniform"
  Varying,      // "varying"
  Vertex,       // "vertex"
  FaceVarying,  // "faceVarying"
  Invalid
};

enum class ListEditQual {
  ResetToExplicit,  // "unqualified"(no qualifier)
  Append,           // "append"
  Add,              // "add"
  Delete,           // "delete"
  Prepend,          // "prepend"
  Invalid
};

enum class Axis { X, Y, Z, Invalid };

// For PrimSpec
enum class Specifier {
  Def,  // 0
  Over,
  Class,
  Invalid
};

enum class Permission {
  Public,  // 0
  Private,
  Invalid
};

enum class Variability {
  Varying,  // 0
  Uniform,
  Config,
  Invalid
};

///
/// We don't need the performance for USDZ, so use naiive implementation
/// to represent Path.
/// Path is something like Unix path, delimited by `/`, ':' and '.'
///
/// Example:
///
/// `/muda/bora.dora` : prim_part is `/muda/bora`, prop_part is `.dora`.
///
/// ':' is a namespce delimiter(example `input:muda`).
///
/// Limitations:
///
/// Relational attribute path(`[` `]`. e.g. `/muda/bora[/ari].dora`) is not
/// supported.
///
/// variant chars('{' '}') is not supported.
/// '..' is not supported
///
/// and have more limitatons.
///
class Path {
 public:
  Path() : valid(false) {}
  Path(const std::string &prim)
      : prim_part(prim), local_part(prim), valid(true) {}
  // Path(const std::string &prim, const std::string &prop)
  //    : prim_part(prim), prop_part(prop) {}

  Path(const Path &rhs) = default;

  Path &operator=(const Path &rhs) {
    this->valid = rhs.valid;

    this->prim_part = rhs.prim_part;
    this->prop_part = rhs.prop_part;
    this->local_part = rhs.local_part;

    return (*this);
  }

  std::string full_path_name() const {
    std::string s;
    if (!valid) {
      s += "INVALID#";
    }

    s += prim_part;
    if (prop_part.empty()) {
      return s;
    }

    s += "." + prop_part;

    return s;
  }

  std::string local_path_name() const {
    std::string s;
    if (!valid) {
      s += "INVALID#";
    }

    s += local_part;

    return s;
  }

  std::string GetPrimPart() const { return prim_part; }

  std::string GetPropPart() const { return prop_part; }

  bool IsValid() const { return valid; }

  bool IsEmpty() { return (prim_part.empty() && prop_part.empty()); }

  static Path AbsoluteRootPath() { return Path("/"); }

  void SetLocalPart(const Path &rhs) {
    // assert(rhs.valid == true);

    this->local_part = rhs.local_part;
    this->valid = rhs.valid;
  }

  std::string GetLocalPart() const { return local_part; }

  Path AppendProperty(const std::string &elem) {
    Path p = (*this);

    if (elem.empty()) {
      p.valid = false;
      return p;
    }

    if (elem[0] == '{') {
      // variant chars are not supported
      p.valid = false;
      return p;
    } else if (elem[0] == '[') {
      // relational attrib are not supported
      p.valid = false;
      return p;
    } else if (elem[0] == '.') {
      // std::cerr << "???. elem[0] is '.'\n";
      // For a while, make this valid.
      p.valid = false;
      return p;
    } else {
      p.prop_part = elem;

      return p;
    }
  }

  Path AppendElement(const std::string &elem) {
    Path p = (*this);

    if (elem.empty()) {
      p.valid = false;
      return p;
    }

    if (elem[0] == '{') {
      // variant chars are not supported
      p.valid = false;
      return p;
    } else if (elem[0] == '[') {
      // relational attrib are not supported
      p.valid = false;
      return p;
    } else if (elem[0] == '.') {
      // std::cerr << "???. elem[0] is '.'\n";
      // For a while, make this valid.
      p.valid = false;
      return p;
    } else {
      // std::cout << "elem " << elem << "\n";
      if ((p.prim_part.size() == 1) && (p.prim_part[0] == '/')) {
        p.prim_part += elem;
      } else {
        p.prim_part += '/' + elem;
      }

      return p;
    }
  }

  Path GetParentPrim() const {

    if (!valid) {
      return Path();
    }

    if (IsRootPrim()) {
      return *this;
    }

    size_t n = prim_part.find_last_of('/');
    if (n == std::string::npos) {
      // this should never happen though.
      return Path();
    }

    if (n == 0) {
      // return root
      return Path("/");
    }

    return Path(prim_part.substr(0, n));
  }

  bool IsRootPrim() const {
    if (!valid) {
      return false;
    }

    if ((prim_part.size() == 1) && (prim_part[0] == '/')) {
      return true;
    }

    return false;
  }

 private:
  std::string prim_part;  // full path
  std::string prop_part;  // full path
  std::string local_part;
  bool valid{false};
};

///
/// Split Path by the delimiter(e.g. "/") then create lists.
///
class TokenizedPath {
 public:
  TokenizedPath() {}

  TokenizedPath(const Path &path) {
    std::string s = path.GetPropPart();
    if (s.empty()) {
      // ???
      return;
    }

    if (s[0] != '/') {
      // Path must start with "/"
      return;
    }

    s.erase(0, 1);

    char delimiter = '/';
    size_t pos{0};
    while ((pos = s.find(delimiter)) != std::string::npos) {
      std::string token = s.substr(0, pos);
      _tokens.push_back(token);
      s.erase(0, pos + sizeof(char));
    }

    if (!s.empty()) {
      // leaf element
      _tokens.push_back(s);
    }
  }

 private:
  std::vector<std::string> _tokens;
};

class TimeCode {
  TimeCode(double tm = 0.0) : _time(tm) {}

  size_t hash() const { return std::hash<double>{}(_time); }

  double value() const { return _time; }

 private:
  double _time;
};

struct LayerOffset {
  double _offset;
  double _scale;
};

struct Payload {
  std::string _asset_path;
  Path _prim_path;
  LayerOffset _layer_offset;
};

struct Reference {
  std::string asset_path;
  Path prim_path;
  LayerOffset layer_offset;
  value::dict custom_data;
};

//
// Colum-major order(e.g. employed in OpenGL).
// For example, 12th([3][0]), 13th([3][1]), 14th([3][2]) element corresponds to
// the translation.
//
// template <typename T, size_t N>
// struct Matrix {
//  T m[N][N];
//  constexpr static uint32_t n = N;
//};

inline void Identity(value::matrix2d *mat) {
  memset(mat->m, 0, sizeof(value::matrix2d));
  for (size_t i = 0; i < 2; i++) {
    mat->m[i][i] = static_cast<double>(1);
  }
}

inline void Identity(value::matrix3d *mat) {
  memset(mat->m, 0, sizeof(value::matrix3d));
  for (size_t i = 0; i < 3; i++) {
    mat->m[i][i] = static_cast<double>(1);
  }
}

inline void Identity(value::matrix4d *mat) {
  memset(mat->m, 0, sizeof(value::matrix4d));
  for (size_t i = 0; i < 4; i++) {
    mat->m[i][i] = static_cast<double>(1);
  }
}

// ret = m x n
template <typename MTy, typename STy, size_t N>
MTy Mult(MTy &m, MTy &n) {
  MTy ret;
  memset(ret.m, 0, sizeof(MTy));

  for (size_t j = 0; j < N; j++) {
    for (size_t i = 0; i < N; i++) {
      STy value = static_cast<STy>(0);
      for (size_t k = 0; k < N; k++) {
        value += m.m[k][i] * n.m[j][k];
      }
      ret.m[j][i] = value;
    }
  }

  return ret;
}

// typedef uint16_t float16;
float half_to_float(value::half h);
value::half float_to_half_full(float f);

struct Extent {
  value::float3 lower{{std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity()}};

  value::float3 upper{{-std::numeric_limits<float>::infinity(),
                       -std::numeric_limits<float>::infinity(),
                       -std::numeric_limits<float>::infinity()}};

  Extent() = default;

  Extent(const value::float3 &l, const value::float3 &u) : lower(l), upper(u) {}

  bool Valid() const {
    if (lower[0] > upper[0]) return false;
    if (lower[1] > upper[1]) return false;
    if (lower[2] > upper[2]) return false;

    return std::isfinite(lower[0]) && std::isfinite(lower[1]) &&
           std::isfinite(lower[2]) && std::isfinite(upper[0]) &&
           std::isfinite(upper[1]) && std::isfinite(upper[2]);
  }

  std::array<std::array<float, 3>, 2> to_array() const {
    std::array<std::array<float, 3>, 2> ret;
    ret[0][0] = lower[0];
    ret[0][1] = lower[1];
    ret[0][2] = lower[2];
    ret[1][0] = upper[0];
    ret[1][1] = upper[1];
    ret[1][2] = upper[2];

    return ret;
  }
};

struct ConnectionPath {
  bool is_input{false};  // true: Input connection. false: Output connection.

  Path path;  // original Path information in USD

  std::string token;  // token(or string) in USD
  int64_t index{-1};  // corresponding array index(e.g. the array index to
                      // `Scene.shaders`)
};

struct Connection {
  int64_t src_index{-1};
  int64_t dest_index{-1};
};

using connection_id_map =
    std::unordered_map<std::pair<std::string, std::string>, Connection>;

// Relation
struct Rel {
  // TODO: Implement
  std::string path;
};

// Variable class for Prim and Attribute Metadataum.
class MetaVariable {
 public:
  std::string type;  // Explicit name of type
  std::string name;
  bool custom{false};

  // using Array = std::vector<Variable>;
  using Object = std::map<std::string, MetaVariable>;

  value::Value value;
  // Array arr_value;
  Object obj_value;
  value::TimeSamples timeSamples;

  MetaVariable &operator=(const MetaVariable &rhs) {
    type = rhs.type;
    name = rhs.name;
    custom = rhs.custom;
    value = rhs.value;
    // arr_value = rhs.arr_value;
    obj_value = rhs.obj_value;

    return *this;
  }

  MetaVariable(const MetaVariable &rhs) {
    type = rhs.type;
    name = rhs.name;
    custom = rhs.custom;
    value = rhs.value;
    obj_value = rhs.obj_value;
  }

  static std::string type_name(const MetaVariable &v) {
    if (!v.type.empty()) {
      return v.type;
    }

    // infer type from value content
    if (v.IsObject()) {
      return "dict";
    } else if (v.IsTimeSamples()) {
      std::string ts_type = "TODO: TimeSample typee";
      // FIXME
#if 0
      auto ts_struct = v.as_timesamples();

      for (const TimeSampleType &item : ts_struct->values) {
        auto tname = value::type_name(item);
        if (tname != "none") {
          return tname;
        }
      }
#endif

      // ??? TimeSamples data contains all `None` values
      return ts_type;

    } else if (v.IsEmpty()) {
      return "none";
    } else {
      return v.value.type_name();
    }
  }

  // template <typename T>
  // bool is() const {
  //   return value.index() == ValueType::index_of<T>();
  // }

  // TODO
  bool IsEmpty() const { return false; }
  bool IsValue() const { return false; }
  // bool IsArray() const {
  // }

  bool IsObject() const { return obj_value.size(); }

  // TODO
  bool IsTimeSamples() const { return false; }

  // For Value
#if 0
  template <typename T>
  const nonstd::optional<T> cast() const {
    printf("cast\n");
    if (IsValue()) {
      std::cout << "type_name = " << Variable::type_name(*this) << "\n";
      const T *p = nonstd::get_if<T>(&value);
      printf("p = %p\n", static_cast<const void *>(p));
      if (p) {
        return *p;
      } else {
        return nonstd::nullopt;
      }
    }
    return nonstd::nullopt;
  }
#endif

  bool valid() const { return !IsEmpty(); }

  MetaVariable() = default;
  // Variable(std::string ty, std::string n) : type(ty), name(n) {}
  // Variable(std::string ty) : type(ty) {}

  // friend std::ostream &operator<<(std::ostream &os, const Object &obj);
  // friend std::ostream &operator<<(std::ostream &os, const MetaVariable &var);

  // friend std::string str_object(const Object &obj, int indent = 0); // string
  // representation of Object.
};

// Metadata for Prim
struct PrimMeta {
  nonstd::optional<Kind> kind;  // 'kind'
  nonstd::optional<Interpolation> interpolation;  // 'interpolation'
  nonstd::optional<std::map<std::string, MetaVariable>>
      customData;  // `customData`

  std::map<std::string, MetaVariable> meta;  // other meta values
};

// Metadata for Attribute
struct AttrMeta {
  // frequently used items
  // nullopt = not specified in USD data
  nonstd::optional<Interpolation> interpolation;  // 'interpolation'
  nonstd::optional<uint32_t> elementSize;         // usdSkel 'elementSize'
  nonstd::optional<std::map<std::string, MetaVariable>>
      customData;  // `customData`

  std::map<std::string, MetaVariable> meta;  // other meta values
};

// mAttrib is a struct to hold attribute of a property(e.g. primvar)
struct PrimAttrib {
  std::string name;  // attrib name

  std::string type_name;  // name of attrib type(e.g. "float', "color3f")

  ListEditQual list_edit{ListEditQual::ResetToExplicit};

  Variability variability;

  // Interpolation interpolation{Interpolation::Invalid};

  AttrMeta meta;

  //
  // Qualifiers
  //
  bool uniform{false};  // `uniform`

  primvar::PrimVar var;
};

// Attribute or Relation. And has this property is custom or not
// (Need to lookup schema if the property is custom or not for Crate data)
struct Property {
  PrimAttrib attrib;
  Rel rel;

  bool is_rel{false};  // true = Attribute
  bool is_custom{false};

  Property() = default;

  Property(const PrimAttrib &a, bool c) : attrib(a), is_custom(c) {
    is_rel = false;
  }

  Property(PrimAttrib &&a, bool c) : attrib(std::move(a)), is_custom(c) {
    is_rel = false;
  }

  Property(const Rel &r, bool c) : rel(r), is_custom(c) { is_rel = true; }

  bool IsRel() const { return is_rel; }

  bool IsCustom() const { return is_custom; }
};

// Currently for UV texture coordinate
template <typename T>
struct PrimvarReader {
  // const char *output_type = TypeTrait<T>::type_name;
  T fallback_value{};  // fallback value

  ConnectionPath
      varname;  // Name of the primvar to be fetched from the geometry.
};

using PrimvarReader_float = PrimvarReader<float>;
using PrimvarReader_float2 = PrimvarReader<value::float2>;
using PrimvarReader_float3 = PrimvarReader<value::float3>;
using PrimvarReader_float4 = PrimvarReader<value::float4>;
using PrimvarReader_int = PrimvarReader<int>;

using PrimvarReaderType =
    tinyusdz::variant<PrimvarReader_float, PrimvarReader_float2,
                      PrimvarReader_float3, PrimvarReader_float4,
                      PrimvarReader_int>;

// Orient: axis/angle expressed as a quaternion.
// NOTE: no `matrix4f`
using XformOpValueType =
    tinyusdz::variant<float, value::float3, value::quatf, double,
                      value::double3, value::quatd, value::matrix4d>;

struct XformOp {
  enum OpType {
    // Matrix
    TRANSFORM,

    // 3D
    TRANSLATE,
    SCALE,

    // 1D
    ROTATE_X,
    ROTATE_Y,
    ROTATE_Z,

    // 3D
    ROTATE_XYZ,
    ROTATE_XZY,
    ROTATE_YXZ,
    ROTATE_YZX,
    ROTATE_ZXY,
    ROTATE_ZYX,

    // 4D
    ORIENT
  };

  static std::string GetOpTypeName(OpType op) {
    std::string str = "[[InvalidXformOp]]";
    switch (op) {
      case TRANSFORM: {
        str = "xformOp:transform";
        break;
      }
      case TRANSLATE: {
        str = "xformOp:translate";
        break;
      }
      case SCALE: {
        str = "xformOp:scale";
        break;
      }
      case ROTATE_X: {
        str = "xformOp:rotateX";
        break;
      }
      case ROTATE_Y: {
        str = "xformOp:rotateY";
        break;
      }
      case ROTATE_Z: {
        str = "xformOp:rotateZ";
        break;
      }
      case ROTATE_XYZ: {
        str = "xformOp:rotateXYZ";
        break;
      }
      case ROTATE_XZY: {
        str = "xformOp:rotateXZY";
        break;
      }
      case ROTATE_YXZ: {
        str = "xformOp:rotateYXZ";
        break;
      }
      case ROTATE_YZX: {
        str = "xformOp:rotateYZX";
        break;
      }
      case ROTATE_ZXY: {
        str = "xformOp:rotateZXY";
        break;
      }
      case ROTATE_ZYX: {
        str = "xformOp:rotateZYX";
        break;
      }
      case ORIENT: {
        str = "xformOp:orient";
        break;
      }
    }
    return str;
  }

  OpType op;
  std::string suffix;
  XformOpValueType value;  // When you look up the value, select basic type
                           // based on `precision`
};

#if 0
template <typename T>
inline T lerp(const T a, const T b, const double t) {
  return (1.0 - t) * a + t * b;
}

template <typename T>
struct TimeSamples {
  std::vector<double> times;
  std::vector<T> values;
  // TODO: Support `none`

  void Set(T value, double t) {
    times.push_back(t);
    values.push_back(value);
  }

  T Get(double t) const {
    // Linear-interpolation.
    // TODO: Support other interpolation method for example cubic.
    auto it = std::lower_bound(times.begin(), times.end(), t);
    size_t idx0 = size_t(std::max(
        int64_t(0), std::min(int64_t(times.size() - 1),
                             int64_t(std::distance(times.begin(), it - 1)))));
    size_t idx1 = size_t(std::max(
        int64_t(0), std::min(int64_t(times.size() - 1), int64_t(idx0) + 1)));

    double tl = times[idx0];
    double tu = times[idx1];

    double dt = (t - tl);
    if (std::fabs(tu - tl) < std::numeric_limits<double>::epsilon()) {
      // slope is zero.
      dt = 0.0;
    } else {
      dt /= (tu - tl);
    }

    // Just in case.
    dt = std::max(0.0, std::min(1.0, dt));

    const T &p0 = values[idx0];
    const T &p1 = values[idx1];

    const T p = lerp(p0, p1, dt);

    return p;
  }

  bool Valid() const {
    return !times.empty() && (times.size() == values.size());
  }
};
#endif

// Animatable = run-time data structure(e.g. for GeomMesh)
// TimeSample data is splitted into multiple ranges when it contains `None`(Blocked)
//
// e.g.
//
// double radius.timeSamples = { 0: 1.0, 1: None, 2: 3.0 }
//
// in .usd, are splitted into two ranges:
//
// range[0, 1): 1.0
// range[2, inf): 3.0
//
// for Animatable type.

template <typename T>
struct TypedTimeSamples
{
  std::vector<double> times;
  std::vector<T> samples;

  bool valid() const {
    if (times.size() > 0) {
      if (samples.size() == times.size()) {
        return true;
      }
    }

    return false;
  }
};

template <typename T>
struct Animatable {
  T value; // scalar

  // TODO: sort by timeframe
  std::vector<TypedTimeSamples<T>> ranges;

  bool IsTimeSampled() const {
    if (ranges.size()) {
      return ranges.begin()->valid();
    }

    return false;
  }

#if 0 // TODO
  T Get() const { return value; }

  T Get(double t) {
    if (IsTimeSampled()) {
      // TODO: lookup value by t
      return timeSamples.Get(t);
    }
    return value;
  }
#endif

  Animatable() {}
  Animatable(T v) : value(v) {}
};

// template<typename T>
// using Animatable = nonstd::variant<T, TimeSampled<T>>;

// Frequently used types
using AnimatableFloat = Animatable<float>;
using AnimatableDouble = Animatable<double>;
using AnimatableExtent = Animatable<Extent>;
using AnimatableVisibility = Animatable<Visibility>;
using AnimatableVec3f = Animatable<value::float3>;
using AnimatableVec3fArray = Animatable<std::vector<value::float3>>;
using AnimatableFloatArray = Animatable<std::vector<float>>;

// Generic "class" Node
// Mostly identical to GPrim
struct Klass {
  std::string name;
  int64_t parent_id{-1};  // Index to parent node

  std::vector<std::pair<ListEditQual, Reference>> references;

  std::map<std::string, Property> props;
};

struct MaterialBindingAPI {
  std::string materialBinding;            // rel material:binding
  std::string materialBindingCorrection;  // rel material:binding:correction

  // TODO: allPurpose, preview, ...
};

//
// Predefined node classes
//

#if 0
struct Xform {
  std::string name;
  int64_t parent_id{-1};  // Index to xform node

  std::vector<XformOp> xformOps;

  Orientation orientation{Orientation::RightHanded};
  AnimatableVisibility visibility{Visibility::Inherited};
  Purpose purpose{Purpose::Default};

  Xform() {}

  ///
  /// Evaluate XformOps
  ///
  bool EvaluateXformOps(value::matrix4d *out_matrix) const;

  ///
  /// Get concatenated matrix.
  ///
  nonstd::optional<value::matrix4d> GetMatrix() const {
    if (_dirty) {
      value::matrix4d m;
      if (EvaluateXformOps(&m)) {
        _matrix = m;
        _dirty = false;
      } else {
        // TODO: Report an error.
        return nonstd::nullopt;
      }
    }
    return _matrix;
  }

  mutable bool _dirty{true};
  mutable value::matrix4d _matrix;  // Resulting matrix of evaluated XformOps.
};
#endif

struct UVCoords {
  using UVCoordType =
      tinyusdz::variant<std::vector<value::float2>, std::vector<value::float3>>;

  std::string name;
  UVCoordType buffer;

  Interpolation interpolation{Interpolation::Vertex};
  Variability variability;

  // non-empty when UV has its own indices.
  std::vector<uint32_t> indices;  // UV indices. Usually varying
};



// BlendShapes
// TODO(syoyo): Blendshape
struct BlendShape {
  std::string name;

  std::vector<float> offsets;        // uniform vector3f[]. required property
  std::vector<float> normalOffsets;  // uniform vector3f[]. required property

  std::vector<int>
      pointIndices;  // uniform int[]. optional. vertex indices to the original mesh for each
                     // values in `offsets` and `normalOffsets`.
};

// Skeleton
struct Skeleton {
  std::string name;

  AnimatableExtent extent;

  std::vector<value::matrix4d>
      bindTransforms;  // uniform matrix4d[]. bind-pose transform of each joint in world coordinate.

  std::vector<std::string> jointNames; // uniform token[]
  std::vector<std::string> joints; // uniform token[]

  // rel proxyPrim

  std::vector<value::matrix4d> restTransforms;  // uniform matrix4d[] rest-pose transforms of each
                                                // joint in local coordinate.

  Purpose purpose{Purpose::Default};
  AnimatableVisibility visibility{Visibility::Inherited};

  std::vector<value::token> xformOpOrder;
};

struct SkelRoot {
  std::string name;
  int64_t parent_id{-1};

  AnimatableExtent extent;
  Purpose purpose{Purpose::Default};
  AnimatableVisibility visibility{Visibility::Inherited};

  // NOTE: SkelRoot itself does not have dedicated attributes in the schema.

  // ref proxyPrim
  std::vector<value::token> xformOpOrder;

  int64_t skeleton_id{-1};  // index to scene.skeletons
  // Skeleton skeleton;
};

struct SkelAnimation {
  std::string name;

  std::vector<value::token> blendShapes; // uniform token[]
  std::vector<float> blendShapeWeights; // float[]
  std::vector<value::token> joints; // uniform token[]
  std::vector<value::quatf> rotations;  // quatf[] Joint-local unit quaternion rotations
  std::vector<value::half3>
      scales;  // half3[] Joint-local scaling in 16bit half float. TODO: Use float3 for TinyUSDZ for convenience?
  std::vector<value::float3> translations;  // float3[] Joint-local translation.
};

// PackedJointAnimation is deprecated(Convert to SkelAnimation)
// struct PackedJointAnimation {
// };

// W.I.P.
struct SkelBindingAPI {
  value::matrix4d geomBindTransform;     // primvars:skel:geomBindTransform
  std::vector<int> jointIndices;         // primvars:skel:jointIndices
  std::vector<float> jointWeights;       // primvars:skel:jointWeights
  std::vector<std::string> blendShapes;  // optional?
  std::vector<std::string> joints;       // optional

  int64_t animationSource{
      -1};  // index to Scene.animations. ref skel:animationSource
  int64_t blendShapeTargets{
      -1};  // index to Scene.blendshapes. ref skel:bindShapeTargets
  int64_t skeleton{-1};  // index to Scene.skeletons. // ref skel:skeleton
};

#if 0
// Generic Prim
struct GPrim {
  std::string name;

  int64_t parent_id{-1};  // Index to parent node

  std::string prim_type;  // Primitive type(if specified by `def`)

  // Gprim
  AnimatableExtent extent;  // bounding extent(in local coord?).
  bool doubleSided{false};
  Orientation orientation{Orientation::RightHanded};
  AnimatableVisibility visibility{Visibility::Inherited};
  Purpose purpose{Purpose::Default};
  AnimatableVec3fArray displayColor;    // primvars:displayColor
  AnimatableFloatArray displayOpacity;  // primvars:displaOpacity

  MaterialBindingAPI materialBinding;

  std::map<std::string, Property> props;

  std::map<std::string, value::Value> args;

  bool _valid{true};  // default behavior is valid(allow empty GPrim)

  bool active{true};

  // child nodes
  std::vector<GPrim> children;
};

// GeomSubset
struct GeomSubset {
  enum class ElementType { Face };

  enum class FamilyType {
    Partition,       // 'partition'
    NonOverlapping,  // 'nonOverlapping'
    Unrestricted,    // 'unrestricted' (fallback)
  };

  std::string name;

  int64_t parent_id{-1};  // Index to parent node

  ElementType elementType{ElementType::Face};  // must be face
  FamilyType familyType{FamilyType::Unrestricted};

  nonstd::expected<bool, std::string> SetElementType(const std::string &str) {
    if (str == "face") {
      elementType = ElementType::Face;
      return true;
    }

    return nonstd::make_unexpected("Only `face` is supported for `elementType`, but `" + str + "` specified");
  }

  nonstd::expected<bool, std::string> SetFamilyType(const std::string &str) {
    if (str == "partition") {
      familyType = FamilyType::Partition;
      return true;
    } else if (str == "nonOverlapping") {
      familyType = FamilyType::NonOverlapping;
      return true;
    } else if (str == "unrestricted") {
      familyType = FamilyType::Unrestricted;
      return true;
    }

    return nonstd::make_unexpected("Invalid `familyType` specified: `" + str + "`.");
  }

  std::vector<uint32_t> indices;

  std::map<std::string, PrimAttrib> attribs; // custom Attrs
};

// Polygon mesh geometry
struct GeomMesh : GPrim {
  //
  // Predefined attribs.
  //
  std::vector<value::point3f> points;  // point3f
  nonstd::optional<PrimAttrib> normals;                  // normal3f[]

  //
  // Utility functions
  //

  // Initialize GeomMesh by GPrim(prepend references)
  void Initialize(const GPrim &pprim);

  // Update GeomMesh by GPrim(append references)
  void UpdateBy(const GPrim &pprim);

  size_t GetNumPoints() const;
  size_t GetNumFacevaryingNormals() const;

  // Get `normals` as float3 array + facevarying
  // Return false if `normals` is neither float3[] type nor `varying`
  bool GetFacevaryingNormals(std::vector<float> *v) const;

  // Get `texcoords` as float2 array + facevarying
  // Return false if `texcoords` is neither float2[] type nor `varying`
  bool GetFacevaryingTexcoords(std::vector<float> *v) const;

  // Primary UV coords(TODO: Remove. Read uv coords through PrimVarReader)
  UVCoords st;

  PrimAttrib velocitiess;  // Usually float3[], varying

  std::vector<int32_t> faceVertexCounts;
  std::vector<int32_t> faceVertexIndices;

  //
  // Properties
  //
  // AnimatableExtent extent;  // bounding extent(in local coord?).
  std::string facevaryingLinearInterpolation = "cornerPlus1";
  // AnimatableVisibility visibility{Visibility::Inherited};
  // Purpose purpose{Purpose::Default};

  // Gprim
  // bool doubleSided{false};
  // Orientation orientation{Orientation::RightHanded};
  // AnimatableVec3fArray displayColor; // primvars:displayColor
  // AnimatableFloatArray displayOpacity; // primvars:displaOpacity

  // MaterialBindingAPI materialBinding;

  //
  // SubD attribs.
  //
  std::vector<int32_t> cornerIndices;
  std::vector<float> cornerSharpnesses;
  std::vector<int32_t> creaseIndices;
  std::vector<int32_t> creaseLengths;
  std::vector<float> creaseSharpnesses;
  std::vector<int32_t> holeIndices;
  std::string interpolateBoundary =
      "edgeAndCorner";  // "none", "edgeAndCorner" or "edgeOnly"
  SubdivisionScheme subdivisionScheme{SubdivisionScheme::CatmullClark};

  //
  // GeomSubset
  //
  // uniform token `subsetFamily:materialBind:familyType`
  GeomSubset::FamilyType materialBindFamilyType{
      GeomSubset::FamilyType::Partition};

  std::vector<GeomSubset> geom_subset_children;

  ///
  /// Validate GeomSubset data attached to this GeomMesh.
  ///
  nonstd::expected<bool, std::string> ValidateGeomSubset();

  // List of Primitive attributes(primvars)
  // std::map<std::string, PrimAttrib> attribs;
};
#endif

//
// Similar to Maya's ShadingGroup
//
struct Material {
  std::string name;

  int64_t parent_id{-1};

  std::string outputs_surface;  // Intermediate variable. Path of
                                // `outputs:surface.connect`
  std::string outputs_volume;   // Intermediate variable. Path of
                                // `outputs:volume.connect`

  // Id will be filled after resolving paths
  int64_t surface_shader_id{-1};  // Index to `Scene::shaders`
  int64_t volume_shader_id{-1};   // Index to `Scene::shaders`
  // int64_t displacement_shader_id{-1}; // Index to shader object. TODO(syoyo)
};

// TODO
struct NodeGraph {
  std::string name;

  int64_t parent_id{-1};
};

// result = (texture_id == -1) ? use color : lookup texture
struct Color3OrTexture {
  Color3OrTexture(float x, float y, float z) {
    color[0] = x;
    color[1] = y;
    color[2] = z;
  }

  std::array<float, 3> color{{0.0f, 0.0f, 0.0f}};

  std::string path;  // path to .connect(We only support texture file connection
                     // at the moment)
  int64_t texture_id{-1};

  bool HasTexture() const { return texture_id > -1; }
};

struct FloatOrTexture {
  FloatOrTexture(float x) { value = x; }

  float value{0.0f};

  std::string path;  // path to .connect(We only support texture file connection
                     // at the moment)
  int64_t texture_id{-1};

  bool HasTexture() const { return texture_id > -1; }
};

enum TextureWrap {
  TextureWrapUseMetadata,  // look for wrapS and wrapT metadata in the texture
                           // file itself
  TextureWrapBlack,
  TextureWrapClamp,
  TextureWrapRepeat,
  TextureWrapMirror
};

// For texture transform
// result = in * scale * rotate * translation
struct UsdTranform2d {
  float rotation =
      0.0f;  // counter-clockwise rotation in degrees around the origin.
  std::array<float, 2> scale{{1.0f, 1.0f}};
  std::array<float, 2> translation{{0.0f, 0.0f}};
};

// UsdUvTexture
struct UVTexture {
  std::string asset;  // asset name(usually file path)
  int64_t image_id{
      -1};  // TODO(syoyo): Consider UDIM `@textures/occlusion.<UDIM>.tex@`

  TextureWrap wrapS{};
  TextureWrap wrapT{};

  std::array<float, 4> fallback{
      {0.0f, 0.0f, 0.0f,
       1.0f}};  // fallback color used when texture cannot be read.
  std::array<float, 4> scale{
      {1.0f, 1.0f, 1.0f, 1.0f}};  // scale to be applied to output texture value
  std::array<float, 4> bias{
      {0.0f, 0.0f, 0.0f, 0.0f}};  // bias to be applied to output texture value

  UsdTranform2d texture_transfom;  // texture coordinate orientation.

  // key = connection name: e.g. "outputs:rgb"
  // item = pair<type, name> : example: <"float3", "outputs:rgb">
  std::map<std::string, std::pair<std::string, std::string>> outputs;

  PrimvarReaderType st;  // texture coordinate(`inputs:st`). We assume there is
                         // a connection to this.

  // TODO: orientation?
  // https://graphics.pixar.com/usd/docs/UsdPreviewSurface-Proposal.html#UsdPreviewSurfaceProposal-TextureCoordinateOrientationinUSD
};

// UsdPreviewSurface
// USD's default? PBR shader
// https://graphics.pixar.com/usd/docs/UsdPreviewSurface-Proposal.html
// $USD/pxr/usdImaging/plugin/usdShaders/shaders/shaderDefs.usda
struct PreviewSurface {
  std::string doc;

  //
  // Infos
  //
  std::string info_id;  // `uniform token`

  //
  // Inputs
  //
  // Currently we don't support nested shader description.
  //
  Color3OrTexture diffuseColor{0.18f, 0.18f, 0.18f};
  Color3OrTexture emissiveColor{0.0f, 0.0f, 0.0f};
  int usdSpecularWorkflow{0};  // 0 = metalness workflow, 1 = specular workflow

  // specular workflow
  Color3OrTexture specularColor{0.0f, 0.0f, 0.0f};

  // metalness workflow
  FloatOrTexture metallic{0.0f};

  FloatOrTexture roughness{0.5f};
  FloatOrTexture clearcoat{0.0f};
  FloatOrTexture clearcoatRoughness{0.01f};
  FloatOrTexture opacity{1.0f};
  FloatOrTexture opacityThreshold{0.0f};
  FloatOrTexture ior{1.5f};
  Color3OrTexture normal{0.0f, 0.0f, 1.0f};
  FloatOrTexture displacement{0.0f};
  FloatOrTexture occlusion{1.0f};

  // Blender Specific?
  FloatOrTexture specular{0.5f};

  //
  // Outputs
  //
  int64_t surface_id{-1};       // index to `Scene::shaders`
  int64_t displacement_id{-1};  // index to `Scene::shaders`
};

struct Shader {
  std::string name;

  std::string info_id;  // Shader type.

  // Currently we only support PreviewSurface, UVTexture and
  // PrimvarReader_float2
  tinyusdz::variant<tinyusdz::monostate, PreviewSurface, UVTexture,
                    PrimvarReader_float2>
      value;
};

// USDZ Schemas for AR
// https://developer.apple.com/documentation/arkit/usdz_schemas_for_ar/schema_definitions_for_third-party_digital_content_creation_dcc

// UsdPhysics
struct Preliminary_PhysicsGravitationalForce {
  // physics::gravitatioalForce::acceleration
  value::double3 acceleration{{0.0, -9.81, 0.0}};  // [m/s^2]
};

struct Preliminary_PhysicsMaterialAPI {
  // preliminary:physics:material:restitution
  double restitution;  // [0.0, 1.0]

  // preliminary:physics:material:friction:static
  double friction_static;

  // preliminary:physics:material:friction:dynamic
  double friction_dynamic;
};

struct Preliminary_PhysicsRigidBodyAPI {
  // preliminary:physics:rigidBody:mass
  double mass{1.0};

  // preliminary:physics:rigidBody:initiallyActive
  bool initiallyActive{true};
};

struct Preliminary_PhysicsColliderAPI {
  // preliminary::physics::collider::convexShape
  Path convexShape;
};

struct Preliminary_InfiniteColliderPlane {
  value::double3 position{{0.0, 0.0, 0.0}};
  value::double3 normal{{0.0, 0.0, 0.0}};

  Extent extent;  // [-FLT_MAX, FLT_MAX]

  Preliminary_InfiniteColliderPlane() {
    extent.lower[0] = -(std::numeric_limits<float>::max)();
    extent.lower[1] = -(std::numeric_limits<float>::max)();
    extent.lower[2] = -(std::numeric_limits<float>::max)();
    extent.upper[0] = (std::numeric_limits<float>::max)();
    extent.upper[1] = (std::numeric_limits<float>::max)();
    extent.upper[2] = (std::numeric_limits<float>::max)();
  }
};

// UsdInteractive
struct Preliminary_AnchoringAPI {
  // preliminary:anchoring:type
  std::string type;  // "plane", "image", "face", "none";

  std::string alignment;  // "horizontal", "vertical", "any";

  Path referenceImage;
};

struct Preliminary_ReferenceImage {
  int64_t image_id{-1};  // asset image

  double physicalWidth{0.0};
};

struct Preliminary_Behavior {
  Path triggers;
  Path actions;
  bool exclusive{false};
};

struct Preliminary_Trigger {
  // uniform token info:id
  std::string info;  // Store decoded string from token id
};

struct Preliminary_Action {
  // uniform token info:id
  std::string info;  // Store decoded string from token id

  std::string multiplePerformOperation{
      "ignore"};  // ["ignore", "allow", "stop"]
};

struct Preliminary_Text {
  std::string content;
  std::vector<std::string> font;  // An array of font names

  float pointSize{144.0f};
  float width;
  float height;
  float depth{0.0f};

  std::string wrapMode{"flowing"};  // ["singleLine", "hardBreaks", "flowing"]
  std::string horizontalAlignmment{
      "center"};  // ["left", "center", "right", "justified"]
  std::string verticalAlignmment{
      "middle"};  // ["top", "middle", "lowerMiddle", "baseline", "bottom"]
};

// Simple volume class.
// Currently this is just an placeholder. Not implemented.

struct OpenVDBAsset {
  std::string fieldDataType{"float"};
  std::string fieldName{"density"};
  std::string filePath;  // asset
};

// MagicaVoxel Vox
struct VoxAsset {
  std::string fieldDataType{"float"};
  std::string fieldName{"density"};
  std::string filePath;  // asset
};

struct Volume {
  OpenVDBAsset vdb;
  VoxAsset vox;
};

// `Scope` is uncommon in graphics community, its something like `Group`.
// From USD doc: Scope is the simplest grouping primitive, and does not carry
// the baggage of transformability.
struct Scope {
  std::string name;

  int64_t parent_id{-1};

  AnimatableVisibility visibility{Visibility::Inherited};
  Purpose purpose{Purpose::Default};
};

Interpolation InterpolationFromString(const std::string &v);
Orientation OrientationFromString(const std::string &v);

namespace value {

#include "define-type-trait.inc"

DEFINE_TYPE_TRAIT(Reference, "ref", TYPE_ID_REFERENCE, 1);
DEFINE_TYPE_TRAIT(Specifier, "specifier", TYPE_ID_SPECIFIER, 1);
DEFINE_TYPE_TRAIT(Permission, "permission", TYPE_ID_PERMISSION, 1);
DEFINE_TYPE_TRAIT(Variability, "variability", TYPE_ID_VARIABILITY, 1);

DEFINE_TYPE_TRAIT(Payload, "payload", TYPE_ID_PAYLOAD, 1);
DEFINE_TYPE_TRAIT(LayerOffset, "LayerOffset", TYPE_ID_LAYER_OFFSET, 1);

DEFINE_TYPE_TRAIT(ListOp<value::token>, "ListOpToken", TYPE_ID_LIST_OP_TOKEN,
                  1);
DEFINE_TYPE_TRAIT(ListOp<std::string>, "ListOpString", TYPE_ID_LIST_OP_STRING,
                  1);
DEFINE_TYPE_TRAIT(ListOp<Path>, "ListOpPath", TYPE_ID_LIST_OP_PATH, 1);
DEFINE_TYPE_TRAIT(ListOp<Reference>, "ListOpReference",
                  TYPE_ID_LIST_OP_REFERENCE, 1);
DEFINE_TYPE_TRAIT(ListOp<int32_t>, "ListOpInt", TYPE_ID_LIST_OP_INT, 1);
DEFINE_TYPE_TRAIT(ListOp<uint32_t>, "ListOpUInt", TYPE_ID_LIST_OP_UINT, 1);
DEFINE_TYPE_TRAIT(ListOp<int64_t>, "ListOpInt64", TYPE_ID_LIST_OP_INT64, 1);
DEFINE_TYPE_TRAIT(ListOp<uint64_t>, "ListOpUInt64", TYPE_ID_LIST_OP_UINT64, 1);
DEFINE_TYPE_TRAIT(ListOp<Payload>, "ListOpPayload", TYPE_ID_LIST_OP_PAYLOAD, 1);

// TODO(syoyo): Define as 1D array?
DEFINE_TYPE_TRAIT(std::vector<Path>, "PathVector", TYPE_ID_PATH_VECTOR, 1);
DEFINE_TYPE_TRAIT(std::vector<value::token>, "TokenVector",
                  TYPE_ID_TOKEN_VECTOR, 1);

DEFINE_TYPE_TRAIT(value::TimeSamples, "TimeSamples", TYPE_ID_TIMESAMPLES, 1);


#undef DEFINE_TYPE_TRAIT
#undef DEFINE_ROLE_TYPE_TRAIT

}  // namespace value

// TODO(syoyo): Range, Interval, Rect2i, Frustum, MultiInterval
// and Quaternion?

/*
#define VT_GFRANGE_VALUE_TYPES                 \
((      GfRange3f,           Range3f        )) \
((      GfRange3d,           Range3d        )) \
((      GfRange2f,           Range2f        )) \
((      GfRange2d,           Range2d        )) \
((      GfRange1f,           Range1f        )) \
((      GfRange1d,           Range1d        ))

#define VT_RANGE_VALUE_TYPES                   \
    VT_GFRANGE_VALUE_TYPES                     \
((      GfInterval,          Interval       )) \
((      GfRect2i,            Rect2i         ))

#define VT_QUATERNION_VALUE_TYPES           \
((      GfQuaternion,        Quaternion ))

#define VT_NONARRAY_VALUE_TYPES                 \
((      GfFrustum,           Frustum))          \
((      GfMultiInterval,     MultiInterval))

*/

}  // namespace tinyusdz
