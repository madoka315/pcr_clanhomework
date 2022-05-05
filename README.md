# pcr_clanhomework
![shitcode](https://img.shields.io/badge/-shitcode-yellow)  
pcr查会战作业插件 for Hoshino  
数据来源于：[踩蘑菇花舞攻略组作业网](caimogu.cc/gzlj)
## 使用
1.安装[Hoshino](https://github.com/Ice-Cirno/HoshinoBot)  
2.切换至HoshinoBot/hoshino/module目录下
```git
git clone https://github.com/madoka315/pcr_clanhomework.git
```
3.在hoshino/config/_\_bot__.py中启用该插件  
4.重启Hoshino
## 更新历史
 - v1.0：
 修正下载逻辑错误、阶段信息错误、文字行溢出问题、图片列溢出问题；  
 调整绘制参数；  
 使用缓存图片时，不再转b64；  
 增加作业超出展示上限时的提示（最后绘制一个灰色矩形）
 - v0.2：
 增加无历史作业时的图片提示；  
 修正下载逻辑错误；  
 调整图片质量
 - v0.1：
 基本功能完成
