import os
import shutil
from importlib.resources import files

dst= os.path.join(os.path.expanduser("~"), 'Desktop')+'\\Python与数据分析及可视化教学案例'
src=files('pet.textbook1')
shutil.copytree(src,dst,dirs_exist_ok=True)

