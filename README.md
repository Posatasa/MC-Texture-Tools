# MC-Texture-Tools
一些简易工具用于批量处理MC纹理文件，以便利于MC百科编辑等类似需求

# 使用前准备
- Python 3.8+
- 依赖：Pillow

# 用法
- 切分动态纹理方块/物品的纹理文件：将需要切分的纹理文件（无需mcmeta）放入AnimatedStackCutter_inputs后运行，每个图片的切分结果输出于AnimatedStackCutter_outputs下的同名文件夹，从上到下按阿拉伯数字命名
- 将Blockbench输出的非正方形且无透明边的图片补充为正方形，并缩放至32和128像素：将需要处理的图片放入BlockbenchImageZoomer_inputs后运行，输出于BlockbenchImageZoomer_outputs下
- 对gif进行同上的处理：放入GIFZoomer_inputs，输出于GIFZoomer_outputs
- 将图片拼合为动图（用于动态纹理）：将图片按帧先后顺序（AnimatedStackCutter的输出通常已经满足需要）放入GIF_source，修改GIFGenerator.py中的ticks_per_frame（暂时只能手动设置，未来考虑增加解析mcmeta），运行生成，生成于GIF_Generator下
- 批量放缩图片：将需要放缩的正方形图片放置于Zoom_space下，修改SimpleZoomer.py中的target_size，然后直接批量放缩，覆盖原来的文件
