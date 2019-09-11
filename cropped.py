import json, os, time, chardet, sys, shutil
from PIL import Image
from subprocess import Popen
from tqdm import tqdm
import threading
import queue

# 800 1137
# out_path = 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/00039_crop.jpg'
json_path = 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/results/json'
cropped_path = 'D:/PyStudy/kakuya/cropped'
comic_path = 'D:/PyStudy/kakuya/comic/all'
detected_path = 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/results/img'
threadNum = 3
classes = ['sigonghuiye', 'baiyinyuxing', 'zaobanai', 'shishangyou', 'zianyanzi', 'yijingyemizi', 'baiyingui', 'baiyinfuqin', 'bomuzhu', 'bomunanyou', 'sitiaozhenfei', 'tengyuanqianhua']

# (left_x, top_y, w, h)——ext_output输出格式
# box = (33, 69, 709, 504)

# (left_x, top_y, right_x, low_y)——crop裁剪图格式
# box = (33, 69, 742, 573)

# box(center_x, center_y, w, h)——json文件内格式
# box = (0.484245, 0.282482, 0.886685, 0.443190)

tag = {}
for cl in classes:
	tag[cl] = 0

def tag_num(s):
	global tag
	tag[s] += 1


def crop_img(in_path, out_path, box):
	img = Image.open(in_path)
	size = img.size
	a = (box[0] - box[2]/2)*size[0]
	b = (box[1] - box[3]/2)*size[1]
	c = (box[0] + box[2]/2)*size[0]
	d = (box[1] + box[3]/2)*size[1]
	print(out_path)

	cropped = img.crop((a, b, c, d))
	print('正在裁剪：%s' % out_path)

	cropped.save(out_path)

# size(w,h) box(xmin, xmax, ymin, ymax)——labelImg生成的格式
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

def get_josn(json_path):
	# crop_img(in_path, out_path, box)
	infom = json.load(open(json_path))[0]
	if len(infom['objects']) != 0:
		for obj in infom['objects']:
			global tag
			tag_num(obj['name'])

			tag_path = os.path.join(cropped_path, obj['name'])
			if not os.path.exists(tag_path): 
				os.makedirs(tag_path)

			out_name = '%s/%s-cropped.jpg' % (obj['name'], img_id)
			cropped_out_path = os.path.join(cropped_path, out_name)

			box = (obj['relative_coordinates']['center_x'], obj['relative_coordinates']['center_y'], obj['relative_coordinates']['width'], obj['relative_coordinates']['height'])

			crop_img(in_path, cropped_out_path, box)
		print('%s全部裁剪完成！' % in_path)
	else:
		print('%s无目标！' % json_path)

class threadCropped(threading.Thread):
	def __init__(self, que):
		threading.Thread.__init__(self)
		self.que = que
	def run(self):
		try:
			get_cropped(self.que)
		except Exception as e:
			print(e)
			sys.exit()

def main():
	imgs = os.listdir(comic_path)

	length = len(imgs)
	queList = []
	#将urllist按照线程数目进行切割
	for i in range(threadNum):
		que = []#
		left = i * (length // threadNum)
		if (i+1) * (length // threadNum) < length:
			right = (i+1) * (length // threadNum)
		else:
			right = length
		for img in imgs[left:right]:
			que.append(img)
		queList.append(que)
	threadList = []
	for i in range(threadNum):
		threadList.append(threadCropped(queList[i]))
	for thread in threadList:
		thread.start()
	for thread in threadList:
		thread.join()


imgs = os.listdir(comic_path)

for img in imgs:
	in_path = os.path.join(comic_path, img)
	in_path = in_path.replace('\\', '/')
	print('正在检测：%s' % in_path)

	img_id, fename=os.path.splitext(img)


	# 检测后的图片地址，已在detector.c中修改
	out_path = os.path.join(detected_path, '%s-detected.jpg' % img_id)

	print('正在保存：%s' % out_path)
	if os.path.exists(out_path):
		print('%s已存在！' % out_path)
		continue
	img_json_path = os.path.join(json_path, '%s-info.json' % img_id)


	# pp = Popen(['D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/darknet', 'detector', 'test', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/coco.data', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/yolov3-voc.cfg', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/backup/yolov3-voc_last.weights', in_path, '-thresh', '0.5', '-out', img_json_path, '-dont_show'])
	pp = Popen(['D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/darknet', 'detector', 'test', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/coco.data', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/yolov3-voc.cfg', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/backup/yolov3-voc_last.weights', in_path, '-out', img_json_path, '-dont_show'])

	t0 = time.time()
	while time.time()-t0 < 100:
		ret = pp.poll()
		if not (ret is None):
			break
		time.sleep(1)
	ret = pp.poll()
	if ret is None:
		print('检测失败，强行终止')
		pp.terminate()
	else:
		print('检测成功，所需时间： %ds' % (time.time()-t0))
		get_josn(img_json_path)
print(tag)

# if __name__ == '__main__':
	# main()



# pp = Popen(['D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/darknet', 'detector', 'test', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/coco.data', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/yolov3-voc.cfg', 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/backup/yolov3-voc_last.weights', in_path, '-thresh', '0.5', '-out', img_json_path, '-dont_show'])
# time.sleep(10)
# infom = json.load(open(img_json_path,'r'))[0]
# print(infom)
# s = 'D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/darknet detector test D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/coco.data D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/main/yolov3-voc.cfg D:/AlexeyAB_DarkNet/darknet-master/darknet-master/datasets/backup/yolov3-voc_last.weights D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/002.jpg -thresh 0.5 -out D:/AlexeyAB_DarkNet/darknet-master/darknet-master/build/darknet/x64/results/json/002-info.json -dont_show'
# os.system(s)
