// SPDX-License-Identifier: MIT
// Copyright 2022 - Present, Syoyo Fujita.
#include "value-types.hh"
#include "value-pprint.hh"


namespace tinyusdz {
namespace value {

//base_value::~base_value() {}


#if 0
bool is_float(const any_value &v) {
  if (v.underlying_type_name() == "float") {
    return true;
  }

  return false;
}

bool is_double(const any_value &v) {
  if (v.underlying_type_name() == "double") {
    return true;
  }

  return false;
}

bool is_float(const Value &v) {
  if (v.underlying_type_name() == "float") {
    return true;
  }

  return false;
}

bool is_float2(const Value &v) {
  if (v.underlying_type_name() == "float2") {
    return true;
  }

  return false;
}

bool is_float3(const Value &v) {
  if (v.underlying_type_name() == "float3") {
    return true;
  }

  return false;
}

bool is_float4(const Value &v) {
  if (v.underlying_type_name() == "float4") {
    return true;
  }

  return false;
}

bool is_double(const Value &v) {
  if (v.underlying_type_name() == "double") {
    return true;
  }

  return false;
}

bool is_double2(const Value &v) {
  if (v.underlying_type_name() == "double2") {
    return true;
  }

  return false;
}

bool is_double3(const Value &v) {
  if (v.underlying_type_name() == "double3") {
    return true;
  }

  return false;
}

bool is_double4(const Value &v) {
  if (v.underlying_type_name() == "double4") {
    return true;
  }

  return false;
}
#endif

#if 0 // TODO: Remove
bool Reconstructor::reconstruct(AttribMap &amap) {
  err_.clear();

  staticstruct::Reader r;

#define CONVERT_TYPE_SCALAR(__ty, __value)       \
  case TypeTrait<__ty>::type_id: {               \
    __ty *p = reinterpret_cast<__ty *>(__value); \
    staticstruct::Handler<__ty> _h(p);           \
    return _h.write(&handler);                   \
  }

#define CONVERT_TYPE_1D(__ty, __value)                                     \
  case (TypeTrait<__ty>::type_id | TYPE_ID_1D_ARRAY_BIT): {                \
    std::vector<__ty> *p = reinterpret_cast<std::vector<__ty> *>(__value); \
    staticstruct::Handler<std::vector<__ty>> _h(p);                        \
    return _h.write(&handler);                                             \
  }

#define CONVERT_TYPE_2D(__ty, __value)                               \
  case (TypeTrait<__ty>::type_id | TYPE_ID_2D_ARRAY_BIT): {          \
    std::vector<std::vector<__ty>> *p =                              \
        reinterpret_cast<std::vector<std::vector<__ty>> *>(__value); \
    staticstruct::Handler<std::vector<std::vector<__ty>>> _h(p);     \
    return _h.write(&handler);                                       \
  }

#define CONVERT_TYPE_LIST(__FUNC) \
  __FUNC(half, v)                 \
  __FUNC(half2, v)                \
  __FUNC(half3, v)                \
  __FUNC(half4, v)                \
  __FUNC(int32_t, v)              \
  __FUNC(uint32_t, v)             \
  __FUNC(int2, v)                 \
  __FUNC(int3, v)                 \
  __FUNC(int4, v)                 \
  __FUNC(uint2, v)                \
  __FUNC(uint3, v)                \
  __FUNC(uint4, v)                \
  __FUNC(int64_t, v)              \
  __FUNC(uint64_t, v)             \
  __FUNC(float, v)                \
  __FUNC(float2, v)               \
  __FUNC(float3, v)               \
  __FUNC(float4, v)               \
  __FUNC(double, v)               \
  __FUNC(double2, v)              \
  __FUNC(double3, v)              \
  __FUNC(double4, v)              \
  __FUNC(quath, v)                \
  __FUNC(quatf, v)                \
  __FUNC(quatd, v)                \
  __FUNC(vector3h, v)             \
  __FUNC(vector3f, v)             \
  __FUNC(vector3d, v)             \
  __FUNC(normal3h, v)             \
  __FUNC(normal3f, v)             \
  __FUNC(normal3d, v)             \
  __FUNC(point3h, v)              \
  __FUNC(point3f, v)              \
  __FUNC(point3d, v)              \
  __FUNC(color3f, v)              \
  __FUNC(color3d, v)              \
  __FUNC(color4f, v)              \
  __FUNC(color4d, v)              \
  __FUNC(matrix2d, v)             \
  __FUNC(matrix3d, v)             \
  __FUNC(matrix4d, v)

  bool ret = r.ParseStruct(
      &h,
      [&amap](std::string key, uint32_t flags, uint32_t user_type_id,
              staticstruct::BaseHandler &handler) -> bool {
        std::cout << "key = " << key << ", count = " << amap.attribs.count(key)
                  << "\n";

        if (!amap.attribs.count(key)) {
          if (flags & staticstruct::Flags::Optional) {
            return true;
          } else {
            return false;
          }
        }

        auto &value = amap.attribs[key];
        if (amap.attribs[key].type_id() == user_type_id) {
          void *v = value.value();

          switch (user_type_id) {
            CONVERT_TYPE_SCALAR(bool, v)

            CONVERT_TYPE_LIST(CONVERT_TYPE_SCALAR)
            CONVERT_TYPE_LIST(CONVERT_TYPE_1D)
            CONVERT_TYPE_LIST(CONVERT_TYPE_2D)

            default: {
              std::cerr << "Unsupported type: " << GetTypeName(user_type_id)
                        << "\n";
              return false;
            }
          }
        } else {
          std::cerr << "type: " << amap.attribs[key].type_name() << "(a.k.a "
                    << amap.attribs[key].underlying_type_name()
                    << ") expected but got " << GetTypeName(user_type_id)
                    << " for attribute \"" << key << "\"\n";
          return false;
        }
      },
      &err_);

  return ret;

#undef CONVERT_TYPE_SCALAR
#undef CONVERT_TYPE_1D
#undef CONVERT_TYPE_2D
#undef CONVERT_TYPE_LIST
}
#endif

nonstd::optional<std::string> TryGetTypeName(uint32_t tyid) {
#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wexit-time-destructors"
#endif

  static std::map<uint32_t, std::string> m;

#ifdef __clang__
#pragma clang diagnostic pop
#endif

  if (m.empty()) {
    // initialize
    m[TYPE_ID_BOOL] = TypeTrait<bool>::type_name();
    m[TYPE_ID_UCHAR] = TypeTrait<uint8_t>::type_name();
    m[TYPE_ID_HALF] = TypeTrait<value::half>::type_name();
    m[TYPE_ID_INT32] = TypeTrait<int32_t>::type_name();
    m[TYPE_ID_UINT32] = TypeTrait<uint32_t>::type_name();

    m[TYPE_ID_VECTOR3H] = TypeTrait<vector3h>::type_name();
    m[TYPE_ID_VECTOR3F] = TypeTrait<vector3f>::type_name();
    m[TYPE_ID_VECTOR3D] = TypeTrait<vector3d>::type_name();

    m[TYPE_ID_POINT3H] = TypeTrait<point3h>::type_name();
    m[TYPE_ID_POINT3F] = TypeTrait<point3f>::type_name();
    m[TYPE_ID_POINT3D] = TypeTrait<point3d>::type_name();

    m[TYPE_ID_NORMAL3H] = TypeTrait<normal3h>::type_name();
    m[TYPE_ID_NORMAL3F] = TypeTrait<normal3f>::type_name();
    m[TYPE_ID_NORMAL3D] = TypeTrait<normal3d>::type_name();

    m[TYPE_ID_COLOR3F] = TypeTrait<color3f>::type_name();
    m[TYPE_ID_COLOR3D] = TypeTrait<color3d>::type_name();
    m[TYPE_ID_COLOR4F] = TypeTrait<color4f>::type_name();
    m[TYPE_ID_COLOR4D] = TypeTrait<color4d>::type_name();

    m[TYPE_ID_HALF2] = TypeTrait<value::half2>::type_name();
    m[TYPE_ID_HALF3] = TypeTrait<value::half3>::type_name();
    m[TYPE_ID_HALF4] = TypeTrait<value::half4>::type_name();

    m[TYPE_ID_DICT] = TypeTrait<dict>::type_name();

    // TODO: ...

    m[TYPE_ID_INT32 | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<int>>::type_name();
    m[TYPE_ID_FLOAT | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<float>>::type_name();
    m[TYPE_ID_FLOAT2 | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<float2>>::type_name();
    m[TYPE_ID_FLOAT3 | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<float3>>::type_name();
    m[TYPE_ID_FLOAT4 | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<float4>>::type_name();

    m[TYPE_ID_POINT3H | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<point3h>>::type_name();
    m[TYPE_ID_POINT3F | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<point3f>>::type_name();
    m[TYPE_ID_POINT3D | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<point3d>>::type_name();

    m[TYPE_ID_VECTOR3H | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<vector3h>>::type_name();
    m[TYPE_ID_VECTOR3F | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<vector3f>>::type_name();
    m[TYPE_ID_VECTOR3D | TYPE_ID_1D_ARRAY_BIT] =
        TypeTrait<std::vector<vector3d>>::type_name();

    // TODO: ...
  }

  if (!m.count(tyid)) {
    return nonstd::nullopt;
  }

  return m.at(tyid);
}

std::string GetTypeName(uint32_t tyid) {

  auto ret = TryGetTypeName(tyid);

  if (!ret) {
    return "(GetTypeName) [[Unknown or unimplemented/unsupported type_id: " +
           std::to_string(tyid) + "]]";
  }

  return ret.value();
}

} // namespace value
} // namespace tinyusdz
