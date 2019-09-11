import xml.etree.ElementTree as ET
import os, random

# box坐标中心化处理
# size(w,h) box(xmin, xmax, ymin, ymax)
def convert(size, box):
	dw = 1./(size[0])
	dh = 1./(size[1])
	x = (box[0] + box[1])/2.0 - 1
	y = (box[2] + box[3])/2.0 - 1
	w = box[1] - box[0]
	h = box[3] - box[2]
	x = x*dw
	w = w*dw
	y = y*dh
	h = h*dh
	return (x,y,w,h)

def tag_num(s):
	global tag
	for cl in classes:
		if s == cl:
			tag[cl] += 1
			break

def random_int_list(start, stop, length):
	start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
	length = int(abs(length)) if length else 0
	random_list = []
	for i in range(length):
		random_list.append(random.randint(start, stop))
	return random_list

# 提取xml文件中的坐标
def convert_xml(in_path, out_path):
	in_file = open(in_path)
	out_file = open(out_path, 'w')

	tree=ET.parse(in_file)
	root = tree.getroot()
	size = root.find('size')
	w = int(size.find('width').text)
	h = int(size.find('height').text)
	if w < 500 or h < 500:
		print(in_path)

	for obj in root.iter('object'):
		difficult = obj.find('difficult').text
		cls = obj.find('name').text
		if cls not in classes or int(difficult)==1:
			continue
		# print(cls)
		tag_num(cls)

		cls_id = classes.index(cls)
		xmlbox = obj.find('bndbox')
		b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
		
		bb = convert((w,h), b)
		

		# print(bb)
		# print('\n')
		out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

xml_path ="D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\label"
txt_path ="D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\labels"
start = 0
xmls = os.listdir(xml_path)
stop = len(xmls)
trian_txt_path = "D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\main\\train.txt"
valid_txt_path = "D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\main\\valid.txt"
classes = ['sigonghuiye', 'baiyinyuxing', 'zaobanai', 'shishangyou', 'zianyanzi', 'yijingyemizi', 'baiyingui', 'baiyinfuqin', 'bomuzhu', 'bomunanyou', 'sitiaozhenfei', 'tengyuanqianhua']
tag = {}

for cl in classes:
	tag[cl] = 0

# 数据集的10%作为recall集
random_list = random_int_list(start, stop, int(0.1 * stop))

train_file = open(trian_txt_path, 'w')
val_file = open(valid_txt_path, 'w')

for index, xml in enumerate(xmls):

	fname, fename=os.path.splitext(xml)
	in_path = os.path.join(xml_path, xml)
	out_path = os.path.join(txt_path, '%s.txt' % fname)
	# convert_xml(in_path, out_path)
	if index in random_list:
		val_file.write('D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\JPEGImages\\%s.jpg' % fname + '\n')

	train_file.write('D:\\AlexeyAB_DarkNet\\darknet-master\\darknet-master\\datasets\\JPEGImages\\%s.jpg' % fname + '\n')
train_file.close()
val_file.close()

# print(tag)

# 带初始训练权重cmd命令
# darknet detector train D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\coco.data D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\yolov3-voc.cfg D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\backup\yolov3-voc_last.weights
# 训练11000次，最后一次权重avrg_loss = 0.52，权重路径：D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\backup\yolov3-voc_last.weights

# 测试
# 修改yolov3-voc.cfg内容
# 命令：（-ext_output:输出预测框坐标值；-width -height：更改检测图片大小，增大尺寸有利于预测小目标；-thresh 改变默认预测置信度阈值，默认为0.24或0.25）
# darknet detector test D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\coco.data D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\yolov3-voc.cfg D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\backup\yolov3-voc_last.weights 00039.jpg -ext_output
# darknet detector test D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\coco.data D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\main\yolov3-voc.cfg D:\AlexeyAB_DarkNet\darknet-master\darknet-master\datasets\backup\yolov3-voc_last.weights 002.jpg -ext_output -thresh 0.5 -out results\json\002-info.json
# 全路径测试代码
# D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/darknet detector test D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/coco.data D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/yolov3-voc.cfg D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/backup/yolov3-voc_last.weights D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/002.jpg -thresh 0.5 -out D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/results/json/002-info.json
