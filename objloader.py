from kivy.logger import Logger


# NOTE: The indices were wrong (in the Sensors implementation)!!!!!!! (6376->4376, 6375->4375)
WAIST_INDICES = [3500, 1336, 917, 916, 919, 918, 665, 662, 657, 654, 631, 632, 720, 799, 796, 890, 889, 3124, 3018, \
        3019, 3502, 6473, 6474, 6545, 4376, 4375, 4284, 4285, 4208, 4120, 4121, 4142, 4143, 4150, 4151, 4406, 4405, \
        4403, 4402, 4812]

CHEST_INDICES = [3076, 2870, 1254, 1255, 1349, 1351, 3033, 3030, 3037, 3034, 3039, 611, 2868, 2864, 2866, 1760, 1419, 741, \
        738, 759, 2957, 2907, 1435, 1436, 1437, 1252, 1235, 749, 752, 3015, 4238, 4237, 4718, 4735, 4736, 4909, ]#6366, 6365, 6416, \
        #6415, 6414, 6413, 6412, 6411, 6327, 6328, 4098, 4101, 6485, 6481, 6482, 6477, 6478, 4828, 4825, 4740, 4737, 6332]

CHEST_INDICES2 = [6366, 6365, 6416, \
        6415, 6414, 6413, 6412, 6411, 6327, 6328, 4098, 4101, 6485, 6481, 6482, 6477, 6478, 4828, 4825, 4740, 4737, 6332]

HIP_INDICES = [1806, 1805, 1804, 1803, 1802, 1801, 1800, 1798, 1797, 1796, 1794, 1791, 1788, 1787, 3101, 3114, 3121, \
        3098, 3099, 3159, 6522, 6523, 6542, 6537, 6525, 5252, 5251, 5255, 5256, 5258, 5260, 5261, 5264, 5263, 5266, \
        5265, 5268, 5267]

THIGH_INDICES = [877, 874, 873, 848, 849, 902, 851, 852, 897, 900, 933, 936, 1359, 963, 908, 911, 1366]

CALF_INDICES = [1154, 1372, 1074, 1077, 1470, 1094, 1095, 1473, 1465, 1466, 1108, 1111, 1530, 1089, 1086]

ANKLE_INDICES = [3322, 3323, 3190, 3188, 3185, 3206, 3182, 3183, 3194, 3195, 3196, 3176, 3177, 3193, 3319]

WRIST_INDICES = [1922, 1970, 1969, 2244, 1945, 1943, 1979, 1938, 1935, 2286, 2243, 2242, 1930, 1927, 1926, 1924]

ELBOW_INDICES = [1573, 1915, 1914, 1577, 1576, 1912, 1911, 1624, 1625, 1917, 1611, 1610, 1607, 1608, 1916, 1574]

BICEP_INDICES = [789, 1311, 1315, 1379, 1378, 1394, 1393, 1389, 1388, 1233, 1232, 1385, 1381, 1382, 1397, 1396, 628, 627]

NECK_INDICES = [3068, 1331, 215, 216, 440, 441, 452, 218, 219, 222, 425, 426, 453, 829, 3944, 3921, 3920, 3734, \
        3731, 3730, 3943, 3935, 3934, 3728, 3729, 4807]

HEAD_INDICES = [336, 232, 235, 1, 0, 3, 7, 136, 160, 161, 166, 167, 269, 179, 182, 252, 253, 384, 3765, 3766, 3694, \
        3693, 3782, 3681, 3678, 3671, 3672, 3648, 3518, 3513, 3514, 3515, 3745, 3744]


INDEX_SET_NAMES = [
    'waist',
    'chest',
    'hip',
    'thigh',
    'calf',
    'ankle',
    'wrist',
    'elbow',
    'bicep',
    'neck',
    'head'
]


ALL_INDEX_SETS = [
    WAIST_INDICES,
    CHEST_INDICES,
    CHEST_INDICES2,
    HIP_INDICES,
    THIGH_INDICES,
    CALF_INDICES,
    ANKLE_INDICES,
    WRIST_INDICES,
    ELBOW_INDICES,
    BICEP_INDICES,
    NECK_INDICES,
    HEAD_INDICES
]

INDICES_LENS = [480, 447, 267, 456, 210, 180, 180, 192, 192, 216, 312, 408]


class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.vertices = []
        self.indices = []
        self.smpl_faces_data = [[] for _ in range(len(ALL_INDEX_SETS))]


class ObjFile:
    def finish_object(self):
        mesh = MeshData()
        idx = 0
        for f in self.faces:
            verts = f[0]
            norms = f[1]
            tcs = f[2]
            
            triangle_data = []
            current_index_set_idx = -1
            for i in range(3):
                # get normal components
                n = (0.0, 0.0, 0.0)
                if norms[i] != -1:
                    n = self.normals[norms[i] - 1]

                # get texture coordinate components
                t = (0.0, 0.0)
                if tcs[i] != -1:
                    t = self.texcoords[tcs[i] - 1]

                # get vertex components
                vertex_idx = verts[i] - 1
                v = self.vertices[vertex_idx]

                vertex_data = [v[0], v[1], v[2], n[0], n[1], n[2], t[0], t[1]]
                triangle_data.extend(vertex_data)
                
                for index_set_idx, index_set in enumerate(ALL_INDEX_SETS):
                    if vertex_idx in index_set:
                        current_index_set_idx = index_set_idx

            mesh.vertices.extend(triangle_data)
            if current_index_set_idx != -1:
                mesh.smpl_faces_data[current_index_set_idx].extend(triangle_data)

            tri = [idx, idx + 1, idx + 2]
            mesh.indices.extend(tri)
            idx += 3
            
        self.objects[self._current_object] = mesh
        self.faces = []

    def __init__(self, resource, mode='str', swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.objects = {}
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        self._current_object = 'smpl'
        
        self.obj_material = None

        material = None
        if mode == 'str':
            lines = resource.split('\n')
        else:
            lines = open(resource, 'r').readlines()
        
        lines.append('mtllib monkey.mtl')

        for line in lines:
            if line.startswith('#'):
                continue
            if line.startswith('s'):
                continue
            values = line.split()
            if not values:
                continue
            if values[0] == 'o':
                self.finish_object()
                self._current_object = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(values[1])
            #elif values[0] in ('usemtl', 'usemat'):
            #    material = values[1]
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if int(w[0]) > 6890:
                        print('')
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(-1)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(-1)
                self.faces.append((face, norms, texcoords, material))
        self.finish_object()


def MTL(filename):
    contents = {}
    mtl = None
    #return
    for line in open(filename, "r"):
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        mtl[values[0]] = values[1:]
    return contents

    def __getitem__(self, key):
        return self.contents[key]
    
    def get(self, key, default=None):
        return self.contents.get(key, default)

