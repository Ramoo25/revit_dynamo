import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import XYZ, Line
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ── Входные параметры ──────────────────────────────────────────────────────────
num_segs  = int(IN[0])        # количество отрезков
start_mm  = float(IN[1])      # длина центральной перемычки, мм
gap_mm    = float(IN[2])      # шаг, мм
base_pt   = IN[3]			  # точка старта (внутренняя)
view      = UnwrapElement(IN[4])	# вид на котором размещаем улитку
k = float(IN[5])					# 1-против часовой стрелки, -1 - по часовой

def mm(val):
    return val / 304.8

gap   = mm(gap_mm)
start = mm(start_mm)

bx = mm(base_pt.X)
by = mm(base_pt.Y)
bz = mm(base_pt.Z)

OUT = base_pt.X

segments = []
xi=bx
yi=by
xn=xi
yn=yi-start

xi2=bx+k*gap
yi2=by
xn2=xi2
yn2=yi2-(start+gap)

segments.append(((xi,yi),(xi2,yi2)))


doc = DocumentManager.Instance.CurrentDBDocument

for i in range(2,num_segs+2,1):
	segments.append(((xi, yi), (xn, yn)))
	segments.append(((xi2, yi2), (xn2, yn2)))
	xi = xn
	yi = yn
	xi2 = xn2
	yi2 = yn2
	if i%4 == 0:
		xn = xi+k*gap*(i-1)
		yn = yi
		xn2 = xi2+k*gap*(i+1)
		yn2 = yi2
		continue
	if i%2 == 0:
		xn = xi-k*gap*(i-1)
		yn = yi
		xn2 = xi2-k*gap*(i+1)
		yn2 = yi2
	else:
		xn = xi
		xn2 = xi2
		if (i-5)%4 == 0:
			yn = yi-(start+gap*(i-2))
			yn2 = yi2-(start+gap*i)
		else:
			yn = yi+(start+gap*(i-2))
			yn2 = yi2+(start+gap*i)


TransactionManager.Instance.EnsureInTransaction(doc)

for (x0, y0), (x1, y1) in segments:
    p0 = XYZ(x0 + bx, y0 + by, bz)
    p1 = XYZ(x1 + bx, y1 + by, bz)
    try:
        revit_line  = Line.CreateBound(p0, p1)
        detail_line = doc.Create.NewDetailCurve(view, revit_line)
    except:
        pass
TransactionManager.Instance.TransactionTaskDone()

#OUT = created
