# Kakuya_Cropped
基于AlexeyAB_DarkNet的目标检测python脚本，实现剪下《辉夜大小姐想让我告白》每位角色的部分

一、程序说明

    1.cropped.py是读取自己训练好的目标检测模型检测图片生成的.josn文件里的检测信息，用PIL库裁剪相应目标（不足：每次裁剪都要预加载一次模型，2000+图片裁剪用了两个小时）

    2.label.py为生成标签文件程序，并根据labelImg标记的图片来制作训练集和检验集