import os
# 部署模式 - 如果重型依赖不可用，使用模拟数据
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "false").lower() == "true"

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    if DEPLOYMENT_MODE:
        # 在部署模式下创建模拟的cv2模块
        class MockCV2:
            CAP_PROP_FPS = 5
            CAP_PROP_FRAME_COUNT = 7
            CAP_PROP_FRAME_WIDTH = 3
            CAP_PROP_FRAME_HEIGHT = 4
            
            class VideoCapture:
                def __init__(self, path):
                    self.path = path
                
                def isOpened(self):
                    return True
                
                def get(self, prop):
                    if prop == 5:  # CAP_PROP_FPS
                        return 25.0
                    elif prop == 7:  # CAP_PROP_FRAME_COUNT
                        return 1500
                    elif prop == 3:  # CAP_PROP_FRAME_WIDTH
                        return 1920
                    elif prop == 4:  # CAP_PROP_FRAME_HEIGHT
                        return 1080
                    return 0
                
                def read(self):
                    return True, None
                
                def release(self):
                    pass
                
                def set(self, prop, value):
                    return True
        
        cv2 = MockCV2()
        CV2_AVAILABLE = True

import numpy as np
try:
    import librosa
    import soundfile as sf
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    
try:
    from sklearn.cluster import KMeans
    from scipy.spatial.distance import euclidean
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    if DEPLOYMENT_MODE:
        # 模拟sklearn
        class MockKMeans:
            def __init__(self, n_clusters=3, random_state=42):
                self.n_clusters = n_clusters
                self.labels_ = None
                
            def fit(self, data):
                self.labels_ = np.random.randint(0, self.n_clusters, len(data))
                return self
        
        class MockSklearn:
            class cluster:
                KMeans = MockKMeans
        
        import sys
        sys.modules['sklearn'] = MockSklearn()
        sys.modules['sklearn.cluster'] = MockSklearn.cluster()
        
        def euclidean(a, b):
            return np.linalg.norm(np.array(a) - np.array(b))
        
        SKLEARN_AVAILABLE = True

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple, Optional
from tqdm import tqdm

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    """视频分析器 - 集成多种AI分析功能"""
    
    def __init__(self, output_dir: str = "uploads"):
        # 确保使用绝对路径，相对于当前工作目录
        if not Path(output_dir).is_absolute():
            # 如果是相对路径，确保相对于backend目录
            backend_dir = Path(__file__).parent.parent
            self.output_dir = backend_dir / output_dir
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化Whisper模型
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper模型加载成功")
            except Exception as e:
                logger.warning(f"Whisper模型加载失败: {e}")
                self.whisper_model = None
        else:
            logger.warning("Whisper未安装，音频转录功能不可用")
            self.whisper_model = None
        
        # 分析结果
        self.analysis_results = {}

    def analyze_video(self, video_path: str, task_config: Dict[str, bool], 
                     progress_callback=None, task_id: str = None) -> Dict[str, Any]:
        """
        分析视频
        
        Args:
            video_path: 视频文件路径
            task_config: 分析任务配置
            progress_callback: 进度回调函数
            
        Returns:
            分析结果字典
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 如果有task_id，则使用task_id作为文件标识符
        if task_id:
            display_video_path = f"uploads/{task_id}.mp4"  # 标准化的显示路径
        else:
            display_video_path = str(video_path)
        
        results = {
            "video_path": display_video_path,
            "original_video_path": str(video_path),  # 保留原始路径
            "task_id": task_id,
            "analysis_time": datetime.now().isoformat(),
            "segments": [],
            "transitions": [],
            "transcription": {},
            "summary": {}
        }
        
        try:
            # 获取视频基本信息
            video_info = self._get_video_info(video_path)
            results["video_info"] = video_info
            
            if progress_callback:
                progress_callback("10", "获取视频信息完成")
            
            # 1. 视频分割
            if task_config.get("video_segmentation", False):
                logger.info("开始视频分割...")
                segments = self._segment_video(video_path, progress_callback, task_id)
                results["segments"] = segments
                if progress_callback:
                    progress_callback("30", "视频分割完成")
            
            # 2. 转场检测
            if task_config.get("transition_detection", False):
                logger.info("开始转场检测...")
                transitions = self._detect_transitions(video_path, progress_callback)
                results["transitions"] = transitions
                if progress_callback:
                    progress_callback("50", "转场检测完成")
            
            # 3. 音频转录
            if task_config.get("audio_transcription", False):
                logger.info("开始音频转录...")
                transcription = self._transcribe_audio(video_path, progress_callback)
                results["transcription"] = transcription
                if progress_callback:
                    progress_callback("70", "音频转录完成")
            
            # 4. 生成脚本内容（基于转录和分段）
            if results.get("transcription") and results.get("segments"):
                logger.info("开始生成脚本...")
                script_content = self._generate_script_content(results, video_path)
                results["script_content"] = script_content
                
                # 保存脚本文件
                if task_id:
                    script_path = self.output_dir / f"{task_id}_script.md"
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(script_content)
                    results["script_file"] = str(script_path)
                    logger.info(f"脚本文件已生成: {script_path}")
                
                if progress_callback:
                    progress_callback("80", "脚本生成完成")
            
            # 5. 生成分析报告
            if task_config.get("report_generation", False):
                logger.info("开始生成报告...")
                report_path = self._generate_report(results, video_path)
                results["report_path"] = str(report_path)
                if progress_callback:
                    progress_callback("90", "报告生成完成")
            
            if progress_callback:
                progress_callback("100", "分析完成")
                
            logger.info("视频分析完成")
            return results
            
        except Exception as e:
            logger.error(f"视频分析失败: {e}")
            raise
    
    def _get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """获取视频基本信息"""
        try:
            if MOVIEPY_AVAILABLE:
                with VideoFileClip(str(video_path)) as clip:
                    return {
                        "duration": clip.duration,
                        "fps": clip.fps,
                        "size": clip.size,
                        "width": clip.w,
                        "height": clip.h,
                        "audio_fps": clip.audio.fps if clip.audio else None
                    }
            else:
                # 使用OpenCV获取视频信息
                cap = cv2.VideoCapture(str(video_path))
                if not cap.isOpened():
                    return {}
                    
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                cap.release()
                
                return {
                    "duration": duration,
                    "fps": fps,
                    "size": [width, height],
                    "width": width,
                    "height": height,
                    "audio_fps": 44100
                }
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {}
    
    def _segment_video(self, video_path: Path, progress_callback=None, task_id: str = None) -> List[Dict]:
        """视频分割 - 基于场景变化"""
        segments = []
        
        print(f"🔍 AI分析器 _segment_video 被调用！视频路径: {video_path}")
        
        # 部署模式下返回模拟数据
        if DEPLOYMENT_MODE and not CV2_AVAILABLE:
            logger.info("部署模式：返回模拟视频分段数据")
            if progress_callback:
                progress_callback("25", "生成模拟分段数据")
            
            # 生成3个模拟片段
            mock_segments = [
                {
                    "segment_id": 1,
                    "start_time": 0.0,
                    "end_time": 30.0,
                    "duration": 30.0,
                    "scene_type": "开场介绍",
                    "frame_count": 750,
                    "composition_analysis": "中心构图，主体突出，背景简洁",
                    "camera_movement": "固定镜头，平稳拍摄",
                    "theme_analysis": "展示开场内容，氛围轻松",
                    "critical_review": "此片段作为开场，有效建立了整体氛围",
                    "transcript_text": "",
                    "thumbnail_url": None,
                    "gif_url": None
                },
                {
                    "segment_id": 2,
                    "start_time": 30.0,
                    "end_time": 90.0,
                    "duration": 60.0,
                    "scene_type": "主要内容",
                    "frame_count": 1500,
                    "composition_analysis": "三分法构图，层次丰富",
                    "camera_movement": "缓慢推进，增强参与感",
                    "theme_analysis": "深入展示核心内容，信息密集",
                    "critical_review": "此片段是整个视频的重点，信息传达效果良好",
                    "transcript_text": "",
                    "thumbnail_url": None,
                    "gif_url": None
                },
                {
                    "segment_id": 3,
                    "start_time": 90.0,
                    "end_time": 120.0,
                    "duration": 30.0,
                    "scene_type": "结尾总结",
                    "frame_count": 750,
                    "composition_analysis": "对称构图，平衡稳定",
                    "camera_movement": "静态镜头，强调稳定感",
                    "theme_analysis": "总结性内容，回顾要点",
                    "critical_review": "此片段很好地总结了前面的内容，形成完整闭环",
                    "transcript_text": "",
                    "thumbnail_url": None,
                    "gif_url": None
                }
            ]
            return mock_segments
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 用于存储帧的特征
            frame_features = []
            timestamps = []
            
            # 每秒采样一帧进行分析
            sample_interval = max(1, int(fps))
            
            frame_idx = 0
            processed_frames = 0
            total_samples = frame_count // sample_interval
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    # 提取帧特征 (颜色直方图)
                    feature = self._extract_frame_features(frame)
                    frame_features.append(feature)
                    timestamps.append(frame_idx / fps)
                    
                    processed_frames += 1
                    if progress_callback and processed_frames % 10 == 0:
                        progress = 10 + (processed_frames / total_samples) * 15  # 10-25%
                        progress_callback(f"{progress:.0f}", f"分析帧 {processed_frames}/{total_samples}")
                
                frame_idx += 1
            
            cap.release()
            
            if len(frame_features) < 2:
                return segments
            
            # 使用K-means聚类进行场景分割
            n_clusters = min(10, len(frame_features) // 5)  # 自适应聚类数量
            if n_clusters > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(frame_features)
                
                # 找到场景边界
                scene_changes = [0]
                for i in range(1, len(labels)):
                    if labels[i] != labels[i-1]:
                        scene_changes.append(i)
                scene_changes.append(len(labels) - 1)
                
                # 生成分割结果
                for i in range(len(scene_changes) - 1):
                    start_idx = scene_changes[i]
                    end_idx = scene_changes[i + 1]
                    
                    # 获取代表性帧进行详细分析
                    mid_frame_idx = (start_idx + end_idx) // 2
                    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_idx * sample_interval)
                    ret, representative_frame = cap.read()
                    
                    # 进行详细分析
                    detailed_analysis = self._analyze_frame_details(representative_frame, timestamps[start_idx], timestamps[end_idx])
                    
                    segment = {
                        "segment_id": i + 1,
                        "start_time": timestamps[start_idx],
                        "end_time": timestamps[end_idx],
                        "duration": timestamps[end_idx] - timestamps[start_idx],
                        "scene_type": f"场景 {i + 1}",
                        "frame_count": (end_idx - start_idx) * sample_interval,
                        # 新增详细分析字段
                        "composition_analysis": detailed_analysis["composition"],
                        "camera_movement": detailed_analysis["camera_movement"],
                        "theme_analysis": detailed_analysis["theme"],
                        "critical_review": detailed_analysis["review"],
                        "transcript_text": ""  # 将在后面添加转录文本
                    }
                    
                    # 生成缩略图和GIF
                    thumbnail_url = None
                    gif_url = None
                    try:
                        if task_id:  # 只有在有task_id时才生成
                            # 创建新的视频捕获对象用于缩略图生成
                            thumbnail_cap = cv2.VideoCapture(str(video_path))
                            thumbnail_url = self._generate_segment_thumbnail(thumbnail_cap, timestamps[start_idx], fps, task_id, i + 1)
                            thumbnail_cap.release()
                            
                            gif_url = self._generate_segment_gif(video_path, timestamps[start_idx], timestamps[end_idx], task_id, i + 1)
                    except Exception as e:
                        logger.warning(f"生成片段{i+1}缩略图/GIF失败: {e}")
                    
                    segment["thumbnail_url"] = thumbnail_url
                    segment["gif_url"] = gif_url
                    
                    segments.append(segment)
                    print(f"🎬 AI分析器生成片段: {segment['segment_id']}, 时长: {segment['duration']:.2f}s, 场景类型: {segment['scene_type']}")
            
            logger.info(f"视频分割完成，共识别 {len(segments)} 个场景")
            return segments
            
        except Exception as e:
            logger.error(f"视频分割失败: {e}")
            return []
    
    def _extract_frame_features(self, frame) -> np.ndarray:
        """提取帧特征"""
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 计算颜色直方图
        hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [50], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [50], [0, 256])
        
        # 归一化并连接特征
        hist_h = hist_h.flatten() / hist_h.sum()
        hist_s = hist_s.flatten() / hist_s.sum()
        hist_v = hist_v.flatten() / hist_v.sum()
        
        feature = np.concatenate([hist_h, hist_s, hist_v])
        return feature
    
    def _analyze_frame_details(self, frame, start_time: float, end_time: float) -> Dict[str, str]:
        """分析帧的详细信息（构图、运镜、主题、简评）"""
        if frame is None:
            return {
                "composition": "无法分析画面构图",
                "camera_movement": "无法分析镜头运动",
                "theme": "无法分析主题内容",
                "review": "无法生成评价"
            }
        
        try:
            # 获取帧的基本信息
            height, width = frame.shape[:2]
            duration = end_time - start_time
            
            # 构图分析（基于图像特征）
            composition = self._analyze_composition(frame, width, height)
            
            # 运镜分析（基于时长和画面特征）
            camera_movement = self._analyze_camera_movement(frame, duration)
            
            # 主题分析（基于画面内容）
            theme = self._analyze_theme(frame, width, height)
            
            # 简评（综合分析）
            review = self._generate_critical_review(composition, camera_movement, theme, duration)
            
            return {
                "composition": composition,
                "camera_movement": camera_movement,
                "theme": theme,
                "review": review
            }
            
        except Exception as e:
            logger.warning(f"详细分析失败: {e}")
            return {
                "composition": "基础画面构图，需要进一步分析",
                "camera_movement": "静态镜头或轻微运动",
                "theme": "内容主题有待识别",
                "review": "镜头具有一定的视觉表现力"
            }
    
    def _analyze_composition(self, frame, width: int, height: int) -> str:
        """分析画面构图"""
        # 计算画面亮度分布
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # 计算对比度
        contrast = np.std(gray)
        
        # 检测边缘密度
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (width * height)
        
        # 分析构图类型
        if edge_density > 0.15:
            if contrast > 60:
                return "复杂构图，画面层次丰富，具有强烈的视觉冲击力"
            else:
                return "精细构图，细节丰富，画面内容充实"
        elif brightness > 180:
            return "明亮构图，画面简洁明了，色调偏亮"
        elif brightness < 80:
            return "暗调构图，营造神秘或沉稳的视觉氛围"
        else:
            return "均衡构图，画面和谐，明暗分布适中"
    
    def _analyze_camera_movement(self, frame, duration: float) -> str:
        """分析镜头运动"""
        # 基于时长判断镜头类型
        if duration < 2:
            return "快切镜头，节奏紧凑，适合展现动感或紧张感"
        elif duration < 5:
            return "标准镜头长度，叙事节奏适中，观众容易接受"
        elif duration < 10:
            return "慢节奏镜头，给观众充分的观察和思考时间"
        else:
            return "长镜头，深度叙事或情感渲染，具有艺术表现力"
    
    def _analyze_theme(self, frame, width: int, height: int) -> str:
        """分析主题内容"""
        # 分析色彩主题
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 计算主要色调
        hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        dominant_hue = np.argmax(hue_hist)
        
        # 计算饱和度
        saturation = np.mean(hsv[:, :, 1])
        
        # 基于色彩分析主题
        if dominant_hue < 30 or dominant_hue > 150:  # 红色系
            if saturation > 100:
                return "热情主题，红色调营造温暖或激烈的情感氛围"
            else:
                return "温和主题，偏暖色调，给人亲切感"
        elif 30 <= dominant_hue <= 90:  # 黄绿色系
            return "自然主题，绿色调营造清新或生机勃勃的感觉"
        elif 90 < dominant_hue <= 130:  # 蓝色系
            return "冷静主题，蓝色调营造宁静或理性的氛围"
        else:
            if saturation > 80:
                return "活跃主题，色彩饱和度高，视觉效果突出"
            else:
                return "中性主题，色彩平和，内容导向型画面"
    
    def _generate_critical_review(self, composition: str, camera_movement: str, theme: str, duration: float) -> str:
        """生成简评"""
        # 基于各项分析生成综合评价
        reviews = []
        
        if "复杂" in composition or "丰富" in composition:
            reviews.append("画面表现力强")
        
        if duration < 3:
            reviews.append("节奏感突出")
        elif duration > 8:
            reviews.append("具有深度叙事价值")
        
        if "热情" in theme or "活跃" in theme:
            reviews.append("情感表达直接")
        elif "自然" in theme or "冷静" in theme:
            reviews.append("氛围营造到位")
        
        if not reviews:
            reviews.append("具有基础的视觉价值")
        
        base_review = "、".join(reviews)
        
        # 添加创作手法评价
        if duration > 6 and ("复杂" in composition or "丰富" in composition):
            technique = "运用长镜头深度构图的拍摄手法"
        elif duration < 3:
            technique = "采用快节奏剪辑手法"
        else:
            technique = "运用标准的影像叙事手法"
        
        return f"此镜头{base_review}，{technique}，在整体叙事中起到重要的视觉支撑作用。"
    
    def _assign_transcription_to_segments(self, results: Dict[str, Any]):
        """为视频片段分配转录文本"""
        segments = results.get("segments", [])
        transcription = results.get("transcription", {})
        transcript_segments = transcription.get("segments", [])
        
        if not transcript_segments:
            return
        
        logger.info("开始为视频片段分配转录文本...")
        
        for segment in segments:
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            
            # 找到时间范围内的转录文本
            segment_texts = []
            for trans_seg in transcript_segments:
                trans_start = trans_seg["start"]
                trans_end = trans_seg["end"]
                
                # 检查时间重叠
                if trans_end >= start_time and trans_start <= end_time:
                    # 有重叠，添加这段文本
                    text = trans_seg["text"].strip()
                    if text:
                        segment_texts.append(text)
            
            # 合并文本
            segment["transcript_text"] = " ".join(segment_texts) if segment_texts else ""
            
        logger.info("转录文本分配完成")
    
    def _generate_script_content(self, results: Dict[str, Any], video_path: Path) -> str:
        """生成完整的脚本内容（Markdown格式）"""
        segments = results.get("segments", [])
        video_info = results.get("video_info", {})
        transcription = results.get("transcription", {})
        
        # 为片段分配转录文本
        self._assign_transcription_to_segments(results)
        
        # 生成Markdown内容
        content = []
        
        # 标题和基本信息
        content.append(f"# 视频脚本分析报告")
        content.append(f"\n**视频文件:** {video_path.name}")
        content.append(f"**总时长:** {video_info.get('duration', 0):.2f} 秒")
        content.append(f"**分析时间:** {results.get('analysis_time', '')[:19]}")
        content.append(f"**片段总数:** {len(segments)} 个")
        content.append("\n---\n")
        
        # 完整转录文本
        if transcription.get("text"):
            content.append("## 完整转录文本\n")
            full_text = transcription["text"].strip()
            # 简单分段处理
            paragraphs = full_text.split("。")
            formatted_paragraphs = []
            
            current_paragraph = ""
            for sentence in paragraphs:
                sentence = sentence.strip()
                if sentence:
                    current_paragraph += sentence + "。"
                    # 每3-4句话分一段
                    if len(current_paragraph) > 150 or sentence.endswith(("？", "！")):
                        formatted_paragraphs.append(current_paragraph.strip())
                        current_paragraph = ""
            
            if current_paragraph.strip():
                formatted_paragraphs.append(current_paragraph.strip())
            
            for para in formatted_paragraphs:
                if para:
                    content.append(f"{para}\n")
            
            content.append("\n---\n")
        
        # 分段详细分析
        content.append("## 分段详细分析\n")
        
        for i, segment in enumerate(segments, 1):
            content.append(f"### 片段 {i} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
            content.append(f"**时长:** {segment['duration']:.1f} 秒\n")
            
            # 文案内容
            if segment.get("transcript_text"):
                content.append(f"**文案内容:**")
                content.append(f"{segment['transcript_text']}\n")
            
            # 构图分析
            content.append(f"**构图分析:**")
            content.append(f"{segment.get('composition_analysis', '暂无分析')}\n")
            
            # 运镜分析
            content.append(f"**运镜分析:**")
            content.append(f"{segment.get('camera_movement', '暂无分析')}\n")
            
            # 主题分析
            content.append(f"**主题分析:**")
            content.append(f"{segment.get('theme_analysis', '暂无分析')}\n")
            
            # 简评
            content.append(f"**专业简评:**")
            content.append(f"{segment.get('critical_review', '暂无评价')}\n")
            
            content.append("---\n")
        
        # 总结
        content.append("## 总体评价\n")
        content.append(self._generate_overall_summary(segments, video_info))
        
        return "\n".join(content)
    
    def _generate_overall_summary(self, segments: List[Dict], video_info: Dict) -> str:
        """生成总体评价"""
        total_duration = video_info.get("duration", 0)
        segment_count = len(segments)
        
        if segment_count == 0:
            return "视频分析数据不足，无法生成总体评价。"
        
        avg_segment_duration = total_duration / segment_count
        
        # 分析节奏特点
        if avg_segment_duration < 3:
            rhythm = "快节奏剪辑风格，镜头切换频繁，适合展现动感内容"
        elif avg_segment_duration < 8:
            rhythm = "中等节奏，剪辑节奏适中，符合观众观看习惯"
        else:
            rhythm = "慢节奏风格，注重深度叙事和情感渲染"
        
        # 分析构图多样性
        composition_types = [seg.get('composition_analysis', '') for seg in segments]
        unique_compositions = len(set(composition_types))
        
        if unique_compositions > segment_count * 0.8:
            composition_variety = "构图变化丰富，视觉表现力强"
        elif unique_compositions > segment_count * 0.5:
            composition_variety = "构图有一定变化，视觉层次较好"
        else:
            composition_variety = "构图相对统一，风格一致性较强"
        
        summary = f"""
本视频共计{total_duration:.1f}秒，分为{segment_count}个片段，平均每个片段{avg_segment_duration:.1f}秒。

**节奏特点:** {rhythm}

**视觉特点:** {composition_variety}

**整体评价:** 该视频在镜头语言运用上{'表现出色' if segment_count > 20 else '基础规范'}，{rhythm.split('，')[0]}，适合{'短视频平台传播' if avg_segment_duration < 5 else '深度内容展示'}。视频的剪辑手法和构图安排显示了创作者{'较高的专业水平' if unique_compositions > segment_count * 0.6 else '基础的制作能力'}。

**建议:** {'保持当前的快节奏风格，可考虑在关键节点适当延长镜头以增强表现力' if avg_segment_duration < 4 else '当前节奏适中，建议在情感高潮部分进一步优化镜头语言' if avg_segment_duration < 8 else '长镜头运用恰当，建议在适当位置增加一些快切镜头以丰富视觉层次'}。
        """.strip()
        
        return summary
    
    def _detect_transitions(self, video_path: Path, progress_callback=None) -> List[Dict]:
        """转场检测"""
        transitions = []
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            prev_frame = None
            frame_idx = 0
            transition_threshold = 0.25  # 转场阈值（降低以检测更多转场）
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # 计算帧间差异
                    diff = self._calculate_frame_difference(prev_frame, frame)
                    
                    # 检测转场
                    if diff > transition_threshold:
                        timestamp = frame_idx / fps
                        transition = {
                            "transition_id": len(transitions) + 1,
                            "timestamp": timestamp,
                            "strength": float(diff),
                            "type": self._classify_transition_type(diff)
                        }
                        transitions.append(transition)
                
                prev_frame = frame.copy()
                frame_idx += 1
                
                if progress_callback and frame_idx % 100 == 0:
                    progress = 30 + (frame_idx / frame_count) * 15  # 30-45%
                    progress_callback(f"{progress:.0f}", f"检测转场 {frame_idx}/{frame_count}")
            
            cap.release()
            
            # 过滤过于密集的转场
            transitions = self._filter_transitions(transitions)
            
            logger.info(f"转场检测完成，共识别 {len(transitions)} 个转场")
            return transitions
            
        except Exception as e:
            logger.error(f"转场检测失败: {e}")
            return []
    
    def _calculate_frame_difference(self, frame1, frame2) -> float:
        """计算两帧之间的差异"""
        # 转换为灰度图
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # 计算直方图
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        
        # 计算相关性
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # 返回差异值（1 - 相关性）
        return 1.0 - correlation
    
    def _classify_transition_type(self, strength: float) -> str:
        """分类转场类型"""
        if strength > 0.7:
            return "硬切"
        elif strength > 0.5:
            return "渐变"
        else:
            return "轻微变化"
    
    def _filter_transitions(self, transitions: List[Dict], min_interval: float = 1.0) -> List[Dict]:
        """过滤过于密集的转场"""
        if not transitions:
            return transitions
        
        filtered = [transitions[0]]
        
        for transition in transitions[1:]:
            last_transition = filtered[-1]
            if transition["timestamp"] - last_transition["timestamp"] >= min_interval:
                filtered.append(transition)
        
        return filtered
    
    def _transcribe_audio(self, video_path: Path, progress_callback=None) -> Dict[str, Any]:
        """音频转录"""
        if not self.whisper_model:
            logger.warning("Whisper模型未加载，跳过音频转录")
            return {"error": "Whisper模型未加载"}
        
        try:
            # 提取音频
            audio_path = self.output_dir / f"{video_path.stem}_audio.wav"
            
            with VideoFileClip(str(video_path)) as video:
                if video.audio is None:
                    return {"error": "视频没有音频轨道"}
                
                # 导出音频
                video.audio.write_audiofile(str(audio_path), verbose=False, logger=None)
            
            if progress_callback:
                progress_callback("55", "音频提取完成")
            
            # 使用Whisper转录
            logger.info("开始音频转录...")
            result = self.whisper_model.transcribe(str(audio_path), language="zh")
            
            if progress_callback:
                progress_callback("65", "音频转录完成")
            
            # 清理临时音频文件
            audio_path.unlink()
            
            # 处理转录结果
            transcription = {
                "text": result["text"],
                "language": result.get("language", "zh"),
                "segments": []
            }
            
            for segment in result.get("segments", []):
                transcription["segments"].append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0)
                })
            
            # 生成字幕文件
            srt_path = self._generate_subtitles(transcription, video_path)
            transcription["subtitle_file"] = str(srt_path)
            
            logger.info(f"音频转录完成，识别文本长度: {len(transcription['text'])}")
            return transcription
            
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            return {"error": str(e)}
    
    def _generate_subtitles(self, transcription: Dict, video_path: Path) -> Path:
        """生成SRT字幕文件"""
        srt_path = self.output_dir / f"{video_path.stem}_subtitles.srt"
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(transcription["segments"]):
                start_time = self._seconds_to_srt_time(segment["start"])
                end_time = self._seconds_to_srt_time(segment["end"])
                
                f.write(f"{i + 1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text']}\n\n")
        
        return srt_path
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """将秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _generate_report(self, results: Dict, video_path: Path) -> Path:
        """生成分析报告PDF"""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.fonts import addMapping
        import platform
        
        report_path = self.output_dir / f"{video_path.stem}_analysis_report.pdf"
        
        # 注册中文字体
        try:
            if platform.system() == "Darwin":  # macOS
                font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
                if not Path(font_path).exists():
                    font_path = "/System/Library/Fonts/STHeiti Light.ttc"
                if not Path(font_path).exists():
                    font_path = "/System/Library/Fonts/Helvetica.ttc"
            elif platform.system() == "Windows":
                font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
                if not Path(font_path).exists():
                    font_path = "C:/Windows/Fonts/simsun.ttc"  # 宋体
            else:  # Linux
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
            if Path(font_path).exists():
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                addMapping('ChineseFont', 0, 0, 'ChineseFont')  # normal
                addMapping('ChineseFont', 1, 0, 'ChineseFont')  # bold
                chinese_font = 'ChineseFont'
            else:
                chinese_font = 'Helvetica'
                logger.warning("未找到中文字体，使用默认字体")
        except Exception as e:
            chinese_font = 'Helvetica'
            logger.warning(f"字体注册失败: {e}")
        
        # 创建PDF文档
        doc = SimpleDocTemplate(str(report_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1,  # 居中对齐
            fontName=chinese_font
        )
        story.append(Paragraph("视频分析报告", title_style))
        story.append(Spacer(1, 20))
        
        # 自定义样式
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontName=chinese_font
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=chinese_font
        )
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontName=chinese_font
        )
        
        # 基本信息
        story.append(Paragraph("基本信息", heading2_style))
        video_info = results.get("video_info", {})
        
        basic_info = [
            ["视频文件", video_path.name],
            ["分析时间", results.get("analysis_time", "")[:19]],
            ["视频时长", f"{video_info.get('duration', 0):.2f} 秒"],
            ["分辨率", f"{video_info.get('width', 0)} x {video_info.get('height', 0)}"],
            ["帧率", f"{video_info.get('fps', 0):.2f} FPS"]
        ]
        
        info_table = Table(basic_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 场景分割结果
        segments = results.get("segments", [])
        if segments:
            story.append(Paragraph("场景分割结果", heading2_style))
            story.append(Paragraph(f"共识别 {len(segments)} 个场景", normal_style))
            story.append(Spacer(1, 10))
            
            # 基础信息表格
            segment_data = [["场景", "开始时间", "结束时间", "时长", "构图特点"]]
            for segment in segments[:10]:  # 只显示前10个
                composition = segment.get('composition_analysis', '标准构图')
                # 截取构图分析的前20个字符
                short_composition = composition[:20] + "..." if len(composition) > 20 else composition
                
                segment_data.append([
                    f"场景 {segment['segment_id']}",
                    f"{segment['start_time']:.2f}s",
                    f"{segment['end_time']:.2f}s",
                    f"{segment['duration']:.2f}s",
                    short_composition
                ])
            
            segment_table = Table(segment_data, colWidths=[0.8*inch, 1*inch, 1*inch, 0.8*inch, 2.4*inch])
            segment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(segment_table)
            
            if len(segments) > 10:
                story.append(Paragraph(f"注：仅显示前10个场景，共有{len(segments)}个场景", normal_style))
            
            story.append(Spacer(1, 15))
            
            # 详细分析（选择前3个场景）
            story.append(Paragraph("重点场景详细分析", heading2_style))
            for i, segment in enumerate(segments[:3]):
                story.append(Paragraph(f"场景 {segment['segment_id']} 详细分析", heading3_style))
                
                detail_data = [
                    ["构图分析", segment.get('composition_analysis', '暂无分析')],
                    ["运镜分析", segment.get('camera_movement', '暂无分析')],
                    ["主题分析", segment.get('theme_analysis', '暂无分析')],
                    ["专业简评", segment.get('critical_review', '暂无简评')]
                ]
                
                detail_table = Table(detail_data, colWidths=[1.5*inch, 4.5*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('LEFTPADDING', (1, 0), (1, -1), 6),
                    ('RIGHTPADDING', (1, 0), (1, -1), 6)
                ]))
                story.append(detail_table)
                story.append(Spacer(1, 12))
            
            story.append(Spacer(1, 15))
        
        # 转场检测结果
        transitions = results.get("transitions", [])
        if transitions:
            story.append(Paragraph("转场检测结果", heading2_style))
            story.append(Paragraph(f"共检测到 {len(transitions)} 个转场", normal_style))
            story.append(Spacer(1, 10))
            
            transition_data = [["转场", "时间点", "强度", "类型"]]
            for transition in transitions[:10]:  # 只显示前10个
                transition_data.append([
                    f"转场 {transition['transition_id']}",
                    f"{transition['timestamp']:.2f}s",
                    f"{transition['strength']:.3f}",
                    transition['type']
                ])
            
            transition_table = Table(transition_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch])
            transition_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(transition_table)
            
            if len(transitions) > 10:
                story.append(Paragraph(f"注：仅显示前10个转场，共有{len(transitions)}个", normal_style))
            story.append(Spacer(1, 20))
        
        # 脚本内容
        script_content = results.get("script_content", "")
        if script_content:
            story.append(Paragraph("脚本内容总结", heading2_style))
            
            # 提取脚本中的总体评价部分
            if "## 总体评价" in script_content:
                summary_start = script_content.find("## 总体评价") + len("## 总体评价")
                summary_content = script_content[summary_start:].strip()
                # 移除Markdown格式
                summary_content = summary_content.replace("**", "").replace("*", "")
                
                story.append(Paragraph("总体评价:", heading3_style))
                # 分段显示
                paragraphs = summary_content.split('\n\n')
                for para in paragraphs[:3]:  # 只显示前3段
                    if para.strip():
                        story.append(Paragraph(para.strip(), normal_style))
                        story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 10))
            story.append(Paragraph("完整脚本请查看单独的脚本文件", normal_style))
        
        # 生成PDF
        doc.build(story)
        logger.info(f"分析报告已生成: {report_path}")
        
        return report_path
    
    def _generate_segment_thumbnail(self, cap, start_time: float, fps: float, task_id: str, segment_id: int) -> str:
        """生成片段缩略图"""
        try:
            # 定位到指定时间的中间帧
            frame_number = int(start_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            if not ret:
                return None
            
            # 生成缩略图文件名
            thumbnail_filename = f"{task_id}_segment_{segment_id}_thumbnail.jpg"
            thumbnail_path = self.output_dir / thumbnail_filename
            
            # 调整图片大小到合适的尺寸（宽度200px）
            height, width = frame.shape[:2]
            new_width = 200
            new_height = int(height * (new_width / width))
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # 保存缩略图
            cv2.imwrite(str(thumbnail_path), resized_frame)
            logger.info(f"生成缩略图: {thumbnail_path}")
            
            # 返回URL路径
            return f"/uploads/{thumbnail_filename}"
        
        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            return None
    
    def _generate_segment_gif(self, video_path: Path, start_time: float, end_time: float, task_id: str, segment_id: int) -> str:
        """生成片段GIF动画"""
        try:
            import subprocess
            import shutil
            
            # 检查是否有ffmpeg
            if not shutil.which("ffmpeg"):
                logger.warning("FFmpeg不可用，跳过GIF生成")
                return None
            
            # 限制GIF时长（最多5秒）和大小
            duration = min(end_time - start_time, 5.0)
            
            # 生成GIF文件名
            gif_filename = f"{task_id}_segment_{segment_id}.gif"
            gif_path = self.output_dir / gif_filename
            
            # 使用FFmpeg生成GIF
            cmd = [
                "ffmpeg", "-y",  # 覆盖输出文件
                "-ss", str(start_time),  # 开始时间
                "-i", str(video_path),  # 输入视频
                "-t", str(duration),  # 持续时间
                "-vf", "scale=320:-1:flags=lanczos,fps=10",  # 缩放和帧率
                "-loop", "0",  # 无限循环
                str(gif_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and gif_path.exists():
                logger.info(f"生成GIF: {gif_path}")
                return f"/uploads/{gif_filename}"
            else:
                logger.warning(f"FFmpeg生成GIF失败: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.warning(f"生成片段{segment_id}GIF超时")
            return None
        except Exception as e:
            logger.error(f"生成片段{segment_id}GIF失败: {e}")
            return None

# 使用示例和测试函数
def test_video_analyzer():
    """测试视频分析器"""
    analyzer = VideoAnalyzer()
    
    # 测试配置
    test_config = {
        "video_segmentation": True,
        "transition_detection": True,
        "audio_transcription": True,
        "report_generation": True
    }
    
    def progress_callback(progress, message):
        print(f"进度: {progress}% - {message}")
    
    # 这里需要提供一个实际的视频文件路径进行测试
    # video_path = "test_video.mp4"
    # results = analyzer.analyze_video(video_path, test_config, progress_callback)
    # print("分析完成:", results)

if __name__ == "__main__":
    test_video_analyzer() 