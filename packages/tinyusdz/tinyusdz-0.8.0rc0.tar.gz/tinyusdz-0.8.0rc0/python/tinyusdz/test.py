import Usd

#, UsdGeom

stage = Usd.Stage.CreateNew('hello.usda')
print(stage)
#UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

#xformPrim = UsdGeom.Xform.Define(stage, '/hello')
#attr = xformPrim.CreateAttribute("test", Sdf.ValueTypeNames.Int)

