import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import os
from datetime import datetime
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RFLearningRoadmapSystem:
    """
    A comprehensive RF IC Design Learning Roadmap System with progress tracking,
    milestone management, analytics, and export capabilities.
    """
    
    def __init__(self, csv_file: str = 'rf_learning_roadmap.csv'):
        """
        Initialize the RF Learning Roadmap System.
        
        Args:
            csv_file (str): Base filename for data storage
        """
        self.csv_file = csv_file
        self.progress_file = csv_file.replace('.csv', '_progress.csv')
        self.milestones_file = csv_file.replace('.csv', '_milestones.csv')
        
        # Define color schemes for different phases (unused in current version but kept for future)
        self.phase_colors = {
            'Foundation': '#3498db',
            'Short-term': '#e74c3c', 
            'Mid-term': '#f39c12',
            'Long-term': '#27ae60',
            'Advanced': '#9b59b6'
        }
        
        # Caches for performance
        self._roadmap_cache: Dict[str, Any] = None
        self.progress: Dict[str, Dict[str, Any]] = {}
        self.milestones: Dict[str, Dict[str, Any]] = {}
        
        # Initialize and load roadmap
        self.roadmap = self._create_comprehensive_roadmap()
        self._load_roadmap_changes()
        self._load_all_data()
        
        logger.info("RF Learning Roadmap System initialized successfully")
        
    def _create_comprehensive_roadmap(self) -> Dict[str, Any]:
        """
        Create a comprehensive learning roadmap with structured phases.
        
        Returns:
            Dict[str, Any]: Complete roadmap structure
        """
        if self._roadmap_cache is not None:
            return self._roadmap_cache
        
        self._roadmap_cache = {
            "Foundation (0-3 months)": {
                "phase": "Foundation",
                "duration_weeks": 12,
                "description": "Essential mathematical and circuit theory foundations",
                "topics": {
                    "Mathematics Fundamentals": {
                        "weeks": 4,
                        "priority": "Critical",
                        "subtopics": [
                            "Complex Analysis & Phasors",
                            "Fourier Transform & Frequency Domain",
                            "Linear Algebra for Circuit Analysis", 
                            "Differential Equations for RLC Circuits",
                            "Probability & Statistics for Noise Analysis"
                        ]
                    },
                    "Circuit Theory Mastery": {
                        "weeks": 4,
                        "priority": "Critical", 
                        "subtopics": [
                            "Network Analysis (Nodal, Mesh)",
                            "Two-port Network Parameters",
                            "S-Parameters Fundamentals",
                            "Smith Chart Applications",
                            "Transmission Line Theory"
                        ]
                    },
                    "Semiconductor Physics": {
                        "weeks": 4,
                        "priority": "High",
                        "subtopics": [
                            "PN Junction Physics",
                            "MOSFET Device Physics",
                            "Small Signal Models",
                            "Parasitic Effects & Modeling",
                            "Process Variations & Corners"
                        ]
                    }
                }
            },
            
            "Short-term: Analog IC Design (3-9 months)": {
                "phase": "Short-term",
                "duration_weeks": 24,
                "description": "Master analog IC design fundamentals and basic RF concepts",
                "topics": {
                    "Analog Building Blocks": {
                        "weeks": 8,
                        "priority": "Critical",
                        "subtopics": [
                            "Current Mirrors & Biasing",
                            "Differential Pairs & Amplifiers",
                            "Cascode Configurations",
                            "Bandgap References",
                            "Voltage/Current References"
                        ]
                    },
                    "Operational Amplifier Design": {
                        "weeks": 6,
                        "priority": "Critical",
                        "subtopics": [
                            "Single-stage OTA Design",
                            "Two-stage Miller Compensated OpAmp",
                            "Folded Cascode OpAmp",
                            "Frequency Compensation Techniques",
                            "Slew Rate & Bandwidth Optimization"
                        ]
                    },
                    "Data Converter Fundamentals": {
                        "weeks": 6,
                        "priority": "High",
                        "subtopics": [
                            "Sample & Hold Circuits",
                            "Flash ADC Architecture",
                            "SAR ADC Design",
                            "Sigma-Delta Basics",
                            "DAC Architectures"
                        ]
                    },
                    "Microwave Engineering Prep": {
                        "weeks": 4,
                        "priority": "High", 
                        "subtopics": [
                            "Network Parameters Deep Dive",
                            "Impedance Matching Networks",
                            "Noise Figure Fundamentals",
                            "Power Transfer & Stability",
                            "Filter Design Basics"
                        ]
                    }
                }
            },
            
            "Mid-term: Advanced Microwave & SerDes (9-18 months)": {
                "phase": "Mid-term", 
                "duration_weeks": 36,
                "description": "Advanced microwave engineering and high-speed digital design",
                "topics": {
                    "Advanced Microwave Engineering": {
                        "weeks": 10,
                        "priority": "Critical",
                        "subtopics": [
                            "Advanced S-Parameter Analysis",
                            "Microstrip & Stripline Design",
                            "Coupler & Power Divider Design", 
                            "Microwave Filter Synthesis",
                            "Nonlinear Circuit Analysis"
                        ]
                    },
                    "High-Speed SerDes Design": {
                        "weeks": 12,
                        "priority": "Critical",
                        "subtopics": [
                            "Signal Integrity Fundamentals",
                            "Jitter Analysis & Modeling",
                            "Equalization Techniques (FFE, DFE)",
                            "Clock Data Recovery (CDR)",
                            "Phase Locked Loops for SerDes",
                            "Eye Diagram Analysis",
                            "Channel Loss Compensation"
                        ]
                    },
                    "EM Simulation Fundamentals": {
                        "weeks": 8,
                        "priority": "High",
                        "subtopics": [
                            "Maxwell Equations Applications",
                            "Finite Element Method (FEM)",
                            "Finite Difference Time Domain (FDTD)",
                            "Method of Moments (MoM)",
                            "HFSS Simulation Setup"
                        ]
                    },
                    "Advanced Layout & Verification": {
                        "weeks": 6,
                        "priority": "High",
                        "subtopics": [
                            "Advanced Layout Techniques",
                            "Parasitic Extraction & Modeling",
                            "EM Verification Flows",
                            "DRC/LVS Advanced Rules",
                            "Layout-dependent Effects"
                        ]
                    }
                }
            },
            
            "Long-term: RF IC Design Mastery (18-30 months)": {
                "phase": "Long-term",
                "duration_weeks": 48, 
                "description": "Deep dive into RF IC design and system integration",
                "topics": {
                    "RF System Architecture": {
                        "weeks": 8,
                        "priority": "Critical",
                        "subtopics": [
                            "Superheterodyne Architecture",
                            "Direct Conversion (Zero-IF)",
                            "Low-IF Architecture",
                            "Software Defined Radio Concepts",
                            "System-level Noise Analysis"
                        ]
                    },
                    "RF Building Blocks Design": {
                        "weeks": 16,
                        "priority": "Critical",
                        "subtopics": [
                            "Low Noise Amplifier (LNA) Design",
                            "Mixer Design (Gilbert Cell, Passive)",
                            "VCO Design & Phase Noise",
                            "Power Amplifier Classes (A,B,C,D,E,F)",
                            "Frequency Synthesizer Design",
                            "Fractional-N PLL Design"
                        ]
                    },
                    "Advanced RF Concepts": {
                        "weeks": 12,
                        "priority": "High", 
                        "subtopics": [
                            "Linearity & Distortion Analysis",
                            "Image Rejection Techniques",
                            "I/Q Mismatch & Calibration",
                            "Multi-standard Receiver Design",
                            "Wideband Circuit Design"
                        ]
                    },
                    "RF System Integration": {
                        "weeks": 8,
                        "priority": "High",
                        "subtopics": [
                            "Package Modeling & Design",
                            "Bond Wire & Flip Chip Effects",
                            "Thermal Management",
                            "Supply Noise & Isolation",
                            "System-level Testing"
                        ]
                    },
                    "Advanced EM Simulation": {
                        "weeks": 4,
                        "priority": "Medium",
                        "subtopics": [
                            "3D EM Simulation Techniques",
                            "Multi-physics Simulation",
                            "Advanced Meshing Strategies", 
                            "Optimization & Tuning"
                        ]
                    }
                }
            },
            
            "Advanced: Cutting-edge Applications (30+ months)": {
                "phase": "Advanced",
                "duration_weeks": 24,
                "description": "Specialized applications and emerging technologies",
                "topics": {
                    "mmWave & 5G/6G Design": {
                        "weeks": 8,
                        "priority": "High",
                        "subtopics": [
                            "mmWave Circuit Design (24-100GHz)",
                            "Phased Array Systems",
                            "Beamforming Techniques", 
                            "Massive MIMO Systems",
                            "5G NR Standard Requirements"
                        ]
                    },
                    "Automotive Radar Systems": {
                        "weeks": 6,
                        "priority": "Medium",
                        "subtopics": [
                            "77GHz Radar IC Design",
                            "FMCW Radar Principles",
                            "Automotive Safety Standards",
                            "Radar Signal Processing",
                            "Multi-radar Interference"
                        ]
                    },
                    "IoT & Low Power RF": {
                        "weeks": 6,
                        "priority": "Medium", 
                        "subtopics": [
                            "Ultra-low Power Design",
                            "Energy Harvesting Circuits",
                            "Wireless Power Transfer",
                            "BLE/WiFi/LoRa Integration",
                            "Battery Management"
                        ]
                    },
                    "Emerging Technologies": {
                        "weeks": 4,
                        "priority": "Low",
                        "subtopics": [
                            "GaN/SiGe Technologies",
                            "Photonic Integration",
                            "Quantum RF Effects",
                            "AI/ML in RF Design"
                        ]
                    }
                }
            }
        }
        return self._roadmap_cache

    def _load_all_data(self) -> None:
        """Load all data from files with error handling."""
        try:
            self._load_progress()
            self._load_milestones()
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")

    def _save_roadmap_changes(self) -> bool:
        """
        Save roadmap changes to a persistent file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            roadmap_file = self.csv_file.replace('.csv', '_roadmap.json')
            roadmap_data = {
                'roadmap': self.roadmap,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '2.0'
            }
            with open(roadmap_file, 'w', encoding='utf-8') as f:
                json.dump(roadmap_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Roadmap changes saved to {roadmap_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving roadmap changes: {e}")
            return False

    def _load_roadmap_changes(self) -> bool:
        """
        Load roadmap changes from persistent file.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            roadmap_file = self.csv_file.replace('.csv', '_roadmap.json')
            if os.path.exists(roadmap_file):
                with open(roadmap_file, 'r', encoding='utf-8') as f:
                    roadmap_data = json.load(f)
                if 'roadmap' in roadmap_data:
                    loaded_roadmap = roadmap_data['roadmap']
                    for phase_name, phase_data in loaded_roadmap.items():
                        if phase_name in self.roadmap:
                            for topic_name, topic_data in phase_data.get('topics', {}).items():
                                self.roadmap[phase_name]['topics'][topic_name] = topic_data
                        else:
                            self.roadmap[phase_name] = phase_data
                    logger.info(f"Roadmap changes loaded from {roadmap_file}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error loading roadmap changes: {e}")
            return False
            
    def _load_progress(self) -> None:
        """Load learning progress from CSV file with resources support."""
        try:
            if os.path.exists(self.progress_file):
                df = pd.read_csv(self.progress_file)
                self.progress = {}
                for _, row in df.iterrows():
                    key = f"{row['Phase']}|{row['Topic']}|{row['Subtopic']}"
                    self.progress[key] = {
                        'status': row['Status'],
                        'completion': row['Completion_Percent'],
                        'notes': row.get('Notes', ''),
                        'resources': row.get('Resources', ''),
                        'last_updated': row['Last_Updated']
                    }
                logger.info(f"Loaded progress for {len(self.progress)} items")
            else:
                self.progress = {}
                logger.info("No existing progress file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            self.progress = {}
    
    def _load_milestones(self) -> None:
        """Load milestone data from CSV file."""
        try:
            if os.path.exists(self.milestones_file):
                df = pd.read_csv(self.milestones_file)
                self.milestones = {}
                for _, row in df.iterrows():
                    key = row['Phase']
                    self.milestones[key] = {
                        'start_date': row['Start_Date'],
                        'target_end_date': row['Target_End_Date'],
                        'actual_end_date': row.get('Actual_End_Date', ''),
                        'status': row['Status']
                    }
                logger.info(f"Loaded {len(self.milestones)} milestones")
            else:
                self.milestones = {}
                logger.info("No existing milestones file found")
        except Exception as e:
            logger.error(f"Error loading milestones: {e}")
            self.milestones = {}
    
    def _save_progress(self) -> bool:
        """
        Save progress to CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    for subtopic in topic_data['subtopics']:
                        key = f"{phase_name}|{topic_name}|{subtopic}"
                        progress_info = self.progress.get(key, {
                            'status': 'Not Started',
                            'completion': 0,
                            'notes': '',
                            'resources': '',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        rows.append({
                            'Phase': phase_name,
                            'Topic': topic_name,
                            'Subtopic': subtopic,
                            'Status': progress_info['status'],
                            'Completion_Percent': progress_info['completion'],
                            'Notes': progress_info['notes'],
                            'Resources': progress_info['resources'],
                            'Priority': topic_data['priority'],
                            'Estimated_Weeks': topic_data['weeks'],
                            'Last_Updated': progress_info['last_updated']
                        })
            df = pd.DataFrame(rows)
            df.to_csv(self.progress_file, index=False)
            logger.info(f"Progress saved to {self.progress_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
            return False
    
    def _save_milestones(self) -> bool:
        """
        Save milestones to CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows = []
            for phase_name, milestone_info in self.milestones.items():
                rows.append({
                    'Phase': phase_name,
                    'Start_Date': milestone_info['start_date'],
                    'Target_End_Date': milestone_info['target_end_date'],
                    'Actual_End_Date': milestone_info.get('actual_end_date', ''),
                    'Status': milestone_info['status']
                })
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(self.milestones_file, index=False)
                logger.info(f"Milestones saved to {self.milestones_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving milestones: {e}")
            return False
    
    def get_progress_info(self, phase: str, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Get progress information for a specific item.
        
        Args:
            phase (str): Phase name
            topic (str): Topic name
            subtopic (str): Subtopic name
            
        Returns:
            Dict[str, Any]: Progress information
        """
        key = f"{phase}|{topic}|{subtopic}"
        progress_info = self.progress.get(key, {
            'status': 'Not Started',
            'completion': 0,
            'notes': '',
            'resources': '',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return progress_info
    
    def set_progress_info(self, phase: str, topic: str, subtopic: str, 
                          status: str, completion: int, notes: str, resources: str = '') -> bool:
        """
        Set progress information for a specific item.
        
        Args:
            phase (str): Phase name
            topic (str): Topic name
            subtopic (str): Subtopic name
            status (str): Status value
            completion (int): Completion percentage
            notes (str): Learning notes
            resources (str): Resources/documents notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{phase}|{topic}|{subtopic}"
            self.progress[key] = {
                'status': status,
                'completion': completion,
                'notes': notes,
                'resources': resources,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self._save_progress()
        except Exception as e:
            logger.error(f"Error setting progress info: {e}")
            return False

    def create_progress_manager(self) -> widgets.Widget:
        """
        Create progress management interface.
        
        Returns:
            widgets.Widget: Progress manager interface
        """
        phase_dropdown = widgets.Dropdown(
            options=['-- Select Phase --'] + list(self.roadmap.keys()),
            value='-- Select Phase --',
            description='Phase:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        topic_dropdown = widgets.Dropdown(
            options=['-- Select Topic --'],
            value='-- Select Topic --',
            description='Topic:',
            layout=widgets.Layout(width='400px'),
            style={'description_width': '80px'}
        )
        
        new_topic_text = widgets.Text(
            placeholder='Nhập tên topic mới...',
            layout=widgets.Layout(width='250px')
        )
        
        topic_weeks = widgets.IntText(
            value=4,
            description='Weeks:',
            layout=widgets.Layout(width='100px'),#100px
            style={'description_width': '50px'} #50px
        )
        
        topic_priority = widgets.Dropdown(
            options=['Critical', 'High', 'Medium', 'Low'],
            value='High',
            description='Priority:',
            layout=widgets.Layout(width='120px'), #120px
            style={'description_width': '60px'}  #60px
        )
        
        add_topic_btn = widgets.Button(
            description='➕ Add Topic',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        
        subtopic_dropdown = widgets.Dropdown(
            options=['-- Select Subtopic --'],
            value='-- Select Subtopic --',
            description='Subtopic:',
            layout=widgets.Layout(width='400px'),
            style={'description_width': '80px'}
        )
        
        new_subtopic_text = widgets.Text(
            placeholder='Nhập tên subtopic mới...',
            layout=widgets.Layout(width='300px')
        )
        
        add_subtopic_btn = widgets.Button(
            description='➕ Add Subtopic',
            button_style='info', 
            layout=widgets.Layout(width='120px')
        )
        
        remove_topic_btn = widgets.Button(
            description='🗑️ Remove Topic',
            button_style='danger',
            layout=widgets.Layout(width='120px'),
            tooltip='Remove selected topic and all its subtopics'
        )
        
        remove_subtopic_btn = widgets.Button(
            description='🗑️ Remove Subtopic',
            button_style='danger',
            layout=widgets.Layout(width='130px'),
            tooltip='Remove selected subtopic only'
        )
        
        status_dropdown = widgets.Dropdown(
            options=['Not Started', 'In Progress', 'Review', 'Completed', 'Skipped'],
            value='Not Started',
            description='Status:',
            layout=widgets.Layout(width='220px'),
            style={'description_width': '60px'}
        )
        
        completion_slider = widgets.IntSlider(
            value=0,
            min=0,
            max=100,
            step=5,
            description='Progress:',
            style={'description_width': '70px'},
            layout=widgets.Layout(width='320px')
        )
        
        notes_area = widgets.Textarea(
            value='',
            placeholder='Chọn subtopic trước để thêm ghi chú học tập...',
            layout=widgets.Layout(width='600px', height='120px'),
            disabled=True
        )
        
        resources_area = widgets.Textarea(
            value='',
            placeholder='Nhập tên tài liệu, đường dẫn, links...',
            layout=widgets.Layout(width='600px', height='80px'),
            disabled=True
        )
        
        enable_notes_btn = widgets.Button(
            description='🔓 Enable Notes',
            button_style='warning',
            layout=widgets.Layout(width='130px'),
            tooltip='Click to manually enable notes if auto-enable fails'
        )
        
        def force_enable_notes(b):
            notes_area.disabled = False
            resources_area.disabled = False
            notes_area.placeholder = 'Notes area manually enabled - you can type now!'
            resources_area.placeholder = 'Resources area manually enabled - add your documents/links!'
            enable_notes_btn.description = '✅ Notes Enabled'
            enable_notes_btn.button_style = 'success'
            enable_notes_btn.disabled = True
            status_indicator.value = "<div style='color: #28a745; padding: 5px;'>🔓 Both notes areas manually enabled</div>"
        
        enable_notes_btn.on_click(force_enable_notes)
        
        save_btn = widgets.Button(
            description='💾 Save Progress',
            button_style='success',
            layout=widgets.Layout(width='140px'),
            tooltip='Save your progress and notes'
        )
        
        selection_info = widgets.HTML(
            value="<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Chọn subtopic để bắt đầu track progress...</i></div>"
        )
        
        status_indicator = widgets.HTML()
        
        def add_new_topic(b):
            selected_phase = phase_dropdown.value
            new_topic_name = new_topic_text.value.strip()
            
            if selected_phase == '-- Select Phase --' or not new_topic_name:
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Phase và nhập tên Topic</div>"
                return
            
            try:
                if new_topic_name in self.roadmap[selected_phase]['topics']:
                    status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Topic '{new_topic_name}' đã tồn tại</div>"
                    return
                
                self.roadmap[selected_phase]['topics'][new_topic_name] = {
                    'weeks': topic_weeks.value,
                    'priority': topic_priority.value,
                    'subtopics': []
                }
                self._save_roadmap_changes()
                
                topics = list(self.roadmap[selected_phase]['topics'].keys())
                topic_dropdown.options = ['-- Select Topic --'] + topics
                topic_dropdown.value = new_topic_name
                new_topic_text.value = ''
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã thêm Topic: {new_topic_name}</div>"
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi thêm topic: {e}</div>"
                logger.error(f"Error adding topic: {e}")
        
        def add_new_subtopic(b):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            new_subtopic_name = new_subtopic_text.value.strip()
            
            if selected_topic == '-- Select Topic --' or not new_subtopic_name:
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Topic và nhập tên Subtopic</div>"
                return
            
            try:
                current_subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                if new_subtopic_name in current_subtopics:
                    status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Subtopic '{new_subtopic_name}' đã tồn tại</div>"
                    return
                
                current_subtopics.append(new_subtopic_name)
                self._save_roadmap_changes()
                
                subtopic_dropdown.options = ['-- Select Subtopic --'] + current_subtopics
                subtopic_dropdown.value = new_subtopic_name
                new_subtopic_text.value = ''
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã thêm Subtopic: {new_subtopic_name}</div>"
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi thêm subtopic: {e}</div>"
                logger.error(f"Error adding subtopic: {e}")
        
        add_topic_btn.on_click(add_new_topic)
        add_subtopic_btn.on_click(add_new_subtopic)
        
        def remove_selected_topic(b):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            
            if selected_topic == '-- Select Topic --':
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Topic để xóa</div>"
                return
            
            try:
                del self.roadmap[selected_phase]['topics'][selected_topic]
                keys_to_remove = [key for key in self.progress if key.startswith(f"{selected_phase}|{selected_topic}|")]
                for key in keys_to_remove:
                    del self.progress[key]
                self._save_roadmap_changes()
                self._save_progress()
                
                topics = list(self.roadmap[selected_phase]['topics'].keys())
                topic_dropdown.options = ['-- Select Topic --'] + topics
                topic_dropdown.value = '-- Select Topic --'
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã xóa Topic: {selected_topic}</div>"
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi xóa topic: {e}</div>"
                logger.error(f"Error removing topic: {e}")
        
        def remove_selected_subtopic(b):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if selected_subtopic == '-- Select Subtopic --':
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Subtopic để xóa</div>"
                return
            
            try:
                self.roadmap[selected_phase]['topics'][selected_topic]['subtopics'].remove(selected_subtopic)
                key = f"{selected_phase}|{selected_topic}|{selected_subtopic}"
                if key in self.progress:
                    del self.progress[key]
                self._save_roadmap_changes()
                self._save_progress()
                
                subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
                subtopic_dropdown.value = '-- Select Subtopic --'
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã xóa Subtopic: {selected_subtopic}</div>"
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi xóa subtopic: {e}</div>"
                logger.error(f"Error removing subtopic: {e}")
        
        remove_topic_btn.on_click(remove_selected_topic)
        remove_subtopic_btn.on_click(remove_selected_subtopic)
        
        def update_topic_options(change):
            selected_phase = change['new']
            if selected_phase == '-- Select Phase --':
                topic_dropdown.options = ['-- Select Topic --']
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            topics = list(self.roadmap[selected_phase]['topics'].keys())
            topic_dropdown.options = ['-- Select Topic --'] + topics
            topic_dropdown.value = '-- Select Topic --'
        
        def update_subtopic_options(change):
            selected_phase = phase_dropdown.value
            selected_topic = change['new']
            if selected_topic == '-- Select Topic --':
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
            subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
            subtopic_dropdown.value = '-- Select Subtopic --'
        
        def update_progress_fields(change=None):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if selected_subtopic == '-- Select Subtopic --':
                notes_area.disabled = True
                resources_area.disabled = True
                notes_area.value = ''
                resources_area.value = ''
                notes_area.placeholder = 'Chọn Phase → Topic → Subtopic để kích hoạt notes...'
                resources_area.placeholder = 'Chọn subtopic để thêm tài liệu...'
                enable_notes_btn.disabled = False
                enable_notes_btn.description = '🔓 Enable Notes'
                enable_notes_btn.button_style = 'warning'
                selection_info.value = "<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Chọn subtopic để bắt đầu track progress...</i></div>"
                return
            
            try:
                progress_info = self.get_progress_info(selected_phase, selected_topic, selected_subtopic)
                status_dropdown.value = progress_info['status']
                completion_slider.value = progress_info['completion']
                notes_area.disabled = False
                resources_area.disabled = False
                notes_area.value = progress_info['notes']
                notes_area.placeholder = f'Nhập ghi chú học tập cho "{selected_subtopic}"...'
                resources_area.value = progress_info.get('resources', '')
                resources_area.placeholder = f'Tài liệu/Links cho "{selected_subtopic}":\n• PDF: filename.pdf\n• Video: https://youtube.com/...\n• Book: Chapter 5, Page 123'
                enable_notes_btn.description = '✅ Auto Enabled'
                enable_notes_btn.button_style = 'success' 
                enable_notes_btn.disabled = True
                
                topic_weeks = self.roadmap[selected_phase]['topics'][selected_topic]['weeks']
                priority = self.roadmap[selected_phase]['topics'][selected_topic]['priority']
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(priority, '#6c757d')
                
                selection_info.value = f"""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 8px; border-left: 4px solid {priority_color};'>
                    <h4 style='margin: 0 0 10px 0; color: #333;'>📖 Đã Chọn</h4>
                    <p style='margin: 0; color: #666;'><strong>Đường dẫn:</strong> {selected_phase.split(':')[0]} → {selected_topic} → {selected_subtopic}</p>
                    <p style='margin: 5px 0 0 0;'><span style='background: {priority_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em;'>{priority}</span> 
                    <strong>Thời gian:</strong> {topic_weeks} tuần | <strong>Cập nhật:</strong> {progress_info['last_updated']}</p>
                </div>
                """
                
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã load dữ liệu cho: {selected_subtopic}</div>"
            except Exception as e:
                logger.error(f"Error in update_progress_fields: {e}")
                notes_area.disabled = False
                resources_area.disabled = False
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Lỗi load dữ liệu nhưng notes đã được kích hoạt</div>"
        
        def save_progress_info(b):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if selected_subtopic == '-- Select Subtopic --':
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn subtopic trước</div>"
                return
            
            try:
                save_btn.description = '💾 Saving...'
                save_btn.disabled = True
                
                success = self.set_progress_info(
                    selected_phase, selected_topic, selected_subtopic,
                    status_dropdown.value, completion_slider.value,
                    notes_area.value, resources_area.value
                )
                
                if success:
                    status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã lưu progress cho: {selected_subtopic}</div>"
                else:
                    status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>❌ Lỗi lưu progress</div>"
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi: {str(e)}</div>"
                logger.error(f"Error in save_progress_info: {e}")
            finally:
                save_btn.description = '💾 Save Progress'
                save_btn.disabled = False
        
        phase_dropdown.observe(update_topic_options, names='value')
        topic_dropdown.observe(update_subtopic_options, names='value')
        subtopic_dropdown.observe(update_progress_fields, names='value')
        save_btn.on_click(save_progress_info)
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📈 Learning Progress Manager</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Track your journey + Add custom topics/subtopics</p>
            </div>
            """),
            
            widgets.VBox([
                widgets.HTML("<h3 style='color: #2e7d32; margin-bottom: 15px;'>🎯 Select & Manage Learning Items</h3>"),
                phase_dropdown,
                widgets.HTML("<div style='height: 8px;'></div>"),
                widgets.HBox([
                    topic_dropdown,
                    widgets.HTML("<div style='width: 10px;'></div>"),
                    widgets.VBox([
                        widgets.HTML("<div style='font-size: 0.9em; color: #666; margin-bottom: 3px;'>Quản Lý Topics:</div>"),
                        widgets.HBox([
                            new_topic_text,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            topic_weeks,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            topic_priority,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            add_topic_btn,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            remove_topic_btn
                        ])
                    ])
                ], layout=widgets.Layout(align_items='flex-end')),
                widgets.HTML("<div style='height: 8px;'></div>"),
                widgets.HBox([
                    subtopic_dropdown,
                    widgets.HTML("<div style='width: 10px;'></div>"),
                    widgets.VBox([
                        widgets.HTML("<div style='font-size: 0.9em; color: #666; margin-bottom: 3px;'>Quản Lý Subtopics:</div>"),
                        widgets.HBox([
                            new_subtopic_text,
                            widgets.HTML("<div style='width: 10px;'></div>"),
                            add_subtopic_btn,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            remove_subtopic_btn
                        ])
                    ])
                ], layout=widgets.Layout(align_items='flex-end')),
                widgets.HTML("<div style='height: 10px;'></div>"),
                selection_info
            ], layout=widgets.Layout(border='2px solid #4CAF50', padding='20px', margin='10px', background_color='#f8fffe')),
            
            widgets.VBox([
                widgets.HTML("<h3 style='color: #1976d2; margin-bottom: 15px;'>📊 Track Progress & Notes</h3>"),
                widgets.HBox([status_dropdown, widgets.HTML("<div style='width: 20px;'></div>"), completion_slider], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>📝 Learning Notes</h4>"),
                widgets.HTML("""
                <div style='background: #fff3cd; padding: 8px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 8px;'>
                    <strong>💡 Ghi chú học tập:</strong> Concepts, insights, questions, challenges...
                </div>
                """),
                notes_area,
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>📚 Tài Liệu & Nguồn Tham Khảo</h4>"),
                widgets.HTML("""
                <div style='background: #e8f5e8; padding: 8px; border-radius: 5px; border-left: 4px solid #28a745; margin-bottom: 8px;'>
                    <strong>📖 Tài liệu:</strong> Tên sách, PDF files, video links, website URLs, page numbers...
                </div>
                """),
                resources_area,
                widgets.HTML("<div style='height: 8px;'></div>"),
                widgets.HBox([
                    enable_notes_btn,
                    widgets.HTML("<div style='width: 15px;'></div>"),
                    widgets.HTML("<span style='color: #666; font-size: 0.9em; font-style: italic;'>👆 Click nếu notes bị disabled</span>")
                ], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 10px;'></div>"),
                widgets.HBox([save_btn, widgets.HTML("<div style='width: 20px;'></div>"), status_indicator], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("""
                <div style='background: #e8f4f8; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;'>
                    <strong>💡 Hướng Dẫn Sử Dụng:</strong><br>
                    <div style='display: flex; gap: 20px; margin-top: 10px;'>
                        <div style='flex: 1;'>
                            <strong>📝 Learning Notes:</strong><br>
                            <span style='font-size: 0.9em; color: #666;'>
                            • Learned about phasor representation<br>
                            • Complex impedance = R + jX<br>
                            • Need to review Euler's formula
                            </span>
                        </div>
                        <div style='flex: 1;'>
                            <strong>📚 Resources:</strong><br>
                            <span style='font-size: 0.9em; color: #666;'>
                            • Book: RF Circuit Design, Ch.3<br>
                            • Video: https://youtu.be/xyz123<br>
                            • PDF: complex_analysis.pdf, p.45-67
                            </span>
                        </div>
                    </div>
                    <div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid #ccc;'>
                        <strong>🗑️ Xóa Items:</strong> Chọn topic/subtopic cần xóa, sau đó click nút Remove tương ứng.<br>
                        <strong>⚠️ Lưu ý:</strong> Xóa topic sẽ xóa luôn tất cả subtopics và progress data liên quan!
                    </div>
                </div>
                """)
            ], layout=widgets.Layout(border='2px solid #2196F3', padding='20px', margin='10px', background_color='#f8fbff'))
        ])


    def create_analytics_dashboard(self) -> widgets.Widget:
        """
        Create comprehensive analytics dashboard.
        
        Returns:
            widgets.Widget: Analytics dashboard
        """
        analytics_output = widgets.Output()
        
        refresh_btn = widgets.Button(
            description='🔄 Refresh Analytics',
            button_style='info',
            layout=widgets.Layout(width='160px'),
            tooltip='Update all analytics and charts'
        )
        
        def generate_analytics(b=None):
            with analytics_output:
                clear_output(wait=True)
                try:
                    print("📊 GENERATING ANALYTICS DASHBOARD...")
                    print("="*60)
                    
                    total_items = completed_items = in_progress_items = review_items = not_started_items = 0
                    phase_stats = {}
                    priority_progress = {p: {'total': 0, 'completed': 0} for p in ['Critical', 'High', 'Medium', 'Low']}
                    roadmap_progress = {}
                    
                    for phase_name, phase_data in self.roadmap.items():
                        phase_total = phase_completed = phase_in_progress = phase_review = phase_not_started = 0
                        topic_progress = {}
                        
                        for topic_name, topic_data in phase_data['topics'].items():
                            priority = topic_data['priority']
                            topic_total = len(topic_data['subtopics'])
                            topic_completed = topic_in_progress = topic_review = topic_not_started = 0
                            subtopic_details = []
                            
                            for subtopic in topic_data['subtopics']:
                                total_items += 1
                                phase_total += 1
                                priority_progress[priority]['total'] += 1
                                progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                                status = progress_info['status']
                                completion = progress_info['completion']
                                
                                # Convert notes and resources to strings to handle float/NaN
                                notes = str(progress_info.get('notes', '')).strip()
                                resources = str(progress_info.get('resources', '')).strip()
                                
                                if status == 'Completed':
                                    completed_items += 1
                                    phase_completed += 1
                                    topic_completed += 1
                                    priority_progress[priority]['completed'] += 1
                                elif status == 'In Progress':
                                    in_progress_items += 1
                                    phase_in_progress += 1
                                    topic_in_progress += 1
                                elif status == 'Review':
                                    review_items += 1
                                    phase_review += 1
                                    topic_review += 1
                                else:
                                    not_started_items += 1
                                    phase_not_started += 1
                                    topic_not_started += 1
                                
                                subtopic_details.append({
                                    'name': subtopic,
                                    'status': status,
                                    'completion': completion,
                                    'has_notes': bool(notes),
                                    'has_resources': bool(resources)
                                })
                            
                            topic_completion_rate = (topic_completed / topic_total * 100) if topic_total > 0 else 0
                            topic_progress[topic_name] = {
                                'total': topic_total,
                                'completed': topic_completed,
                                'in_progress': topic_in_progress,
                                'review': topic_review,
                                'not_started': topic_not_started,
                                'completion_rate': topic_completion_rate,
                                'priority': priority,
                                'weeks': topic_data['weeks'],
                                'subtopics': subtopic_details
                            }
                        
                        phase_completion_rate = (phase_completed / phase_total * 100) if phase_total > 0 else 0
                        phase_stats[phase_name] = {
                            'total': phase_total,
                            'completed': phase_completed,
                            'in_progress': phase_in_progress,
                            'review': phase_review,
                            'not_started': phase_not_started,
                            'completion_rate': phase_completion_rate
                        }
                        
                        roadmap_progress[phase_name] = {
                            'phase_info': phase_data,
                            'phase_stats': phase_stats[phase_name],
                            'topics': topic_progress
                        }
                    
                    overall_completion = (completed_items / total_items * 100) if total_items > 0 else 0
                    
                    print(f"📈 OVERALL PROGRESS SUMMARY")
                    print(f"Total Items: {total_items} | Completed: {completed_items} ({overall_completion:.1f}%)")
                    print(f"In Progress: {in_progress_items} | Review: {review_items} | Not Started: {not_started_items}")
                    print()
                    
                    print("🗺️ DETAILED ROADMAP PROGRESS OVERVIEW")
                    print("="*60)
                    
                    for phase_name, phase_data in roadmap_progress.items():
                        phase_short = phase_name.split(':')[0]
                        phase_stats_data = phase_data['phase_stats']
                        print(f"\n📍 {phase_short} ({phase_stats_data['completion_rate']:.1f}% complete)")
                        print(f"   Progress: {phase_stats_data['completed']}/{phase_stats_data['total']} items")
                        print(f"   Status: {phase_stats_data['in_progress']} in progress, {phase_stats_data['review']} review, {phase_stats_data['not_started']} not started")
                        
                        for topic_name, topic_data in phase_data['topics'].items():
                            completion_rate = topic_data['completion_rate']
                            priority = topic_data['priority']
                            icon = "✅" if completion_rate == 100 else "🔄" if completion_rate > 50 else "🔵" if completion_rate > 0 else "⚪"
                            print(f"     {icon} {topic_name} ({completion_rate:.0f}%) - {priority} Priority")
                            
                            if 0 < completion_rate < 100:
                                completed_subtopics = [s['name'] for s in topic_data['subtopics'] if s['status'] == 'Completed']
                                in_progress_subtopics = [s for s in topic_data['subtopics'] if s['status'] == 'In Progress']
                                
                                if completed_subtopics:
                                    print(f"        ✅ Completed: {', '.join(completed_subtopics[:3])}{'...' if len(completed_subtopics) > 3 else ''}")
                                
                                if in_progress_subtopics:
                                    for subtopic in in_progress_subtopics[:2]:
                                        notes_indicator = "📝" if subtopic['has_notes'] else ""
                                        resources_indicator = "📚" if subtopic['has_resources'] else ""
                                        print(f"        🔄 {subtopic['name']} ({subtopic['completion']}%) {notes_indicator}{resources_indicator}")
                    
                    print(f"\n🎯 PROGRESS BY PRIORITY")
                    print("="*30)
                    for priority, data in priority_progress.items():
                        rate_p = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
                        print(f"{priority:8}: {data['completed']:3}/{data['total']:3} ({rate_p:5.1f}%)")
                    
                    print(f"\n💡 SMART RECOMMENDATIONS")
                    print("="*30)
                    
                    quick_wins = []
                    focus_areas = []
                    
                    for phase_name, phase_data in roadmap_progress.items():
                        for topic_name, topic_data in phase_data['topics'].items():
                            for subtopic in topic_data['subtopics']:
                                if subtopic['status'] == 'Review':
                                    quick_wins.append(f"{subtopic['name']} (Review)")
                                elif subtopic['status'] == 'In Progress' and subtopic['completion'] > 70:
                                    quick_wins.append(f"{subtopic['name']} ({subtopic['completion']}%)")
                                elif subtopic['status'] == 'Not Started' and topic_data['priority'] == 'Critical':
                                    focus_areas.append(f"{subtopic['name']} (Critical)")
                    
                    if quick_wins:
                        print("🎯 Quick Wins (Close to completion):")
                        for item in quick_wins[:5]:
                            print(f"   • {item}")
                    
                    if focus_areas:
                        print("🔥 Critical Focus Areas:")
                        for item in focus_areas[:5]:
                            print(f"   • {item}")
                    
                    notes_count = sum(1 for p in self.progress.values() if str(p.get('notes', '')).strip())
                    resources_count = sum(1 for p in self.progress.values() if str(p.get('resources', '')).strip())
                    
                    print(f"\n📚 LEARNING INSIGHTS")
                    print("="*25)
                    print(f"📝 Items with notes: {notes_count}")
                    print(f"📖 Items with resources: {resources_count}")
                    print(f"💡 Completion rate: {overall_completion:.1f}%")
                    
                    if overall_completion > 75:
                        print("🎉 Excellent progress! You're on track for mastery.")
                    elif overall_completion > 50:
                        print("👍 Good momentum! Keep up the consistent effort.")
                    elif overall_completion > 25:
                        print("📈 Building foundations! Focus on critical items.")
                    else:
                        print("🚀 Getting started! Begin with foundation topics.")
                    
                    print("\n" + "="*60)
                    print("✅ Analytics refresh completed!")
                except Exception as e:
                    print(f"❌ Error generating analytics: {e}")
                    logger.error(f"Analytics generation error: {e}")
        
        refresh_btn.on_click(generate_analytics)
        generate_analytics()  # Initial load
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #6a11cb, #2575fc); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📊 Learning Analytics & Roadmap Progress</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Comprehensive insights with detailed progress tracking</p>
            </div>
            """),
            
            widgets.HBox([
                refresh_btn,
                widgets.HTML("<div style='width: 20px;'></div>"),
                widgets.HTML("<div style='color: #666; font-style: italic; padding: 8px 0;'>💡 Analytics automatically include roadmap progress overview</div>")
            ], layout=widgets.Layout(margin='0 0 15px 0')),
            
            analytics_output
        ])

    

    def display_full_system(self) -> widgets.Widget:
        """
        Display the complete learning roadmap system.
        
        Returns:
            widgets.Widget: Complete system interface
        """
        try:
            tab_contents = [
                self.create_progress_manager(),
                self.create_analytics_dashboard()
            ]
            tab_titles = [
                '📈 Progress Tracker',
                '📊 Analytics & Overview'
            ]
            tabs = widgets.Tab()
            tabs.children = tab_contents
            for i, title in enumerate(tab_titles):
                tabs.set_title(i, title)
            
            header = widgets.HTML(f"""
            <div style='text-align: center; padding: 25px; background: linear-gradient(45deg, #667eea, #764ba2); 
                        color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
                <h1 style='margin: 0 0 10px 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                    🎯 Learning System
                </h1>
                <p style='margin: 5px 0 15px 0; font-size: 1.3em; opacity: 0.95;'>
                    Complete learning management with analytics & progress overview
                </p>
                <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin-top: 15px;'>
                    <div style='display: flex; justify-content: space-around; flex-wrap: wrap;'>
                        <div style='margin: 5px;'><strong>➕ Add Topics</strong><br>Custom content</div>
                        <div style='margin: 5px;'><strong>🗑️ Remove Items</strong><br>Clean management</div>
                        <div style='margin: 5px;'><strong>📝📚 Dual Notes</strong><br>Learning + Resources</div>
                        <div style='margin: 5px;'><strong>📊 Analytics</strong><br>Progress overview</div>
                    </div>
                </div>
            </div>
            """)
            
            total_topics = sum(len(phase_data['topics']) for phase_data in self.roadmap.values())
            total_subtopics = sum(len(topic_data['subtopics']) for phase_data in self.roadmap.values() for topic_data in phase_data['topics'].values())
            
            system_info = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 20px; border-radius: 12px; 
                        margin-bottom: 20px; border: 2px solid #dee2e6;'>
                <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>🎯 Current Status</h4>
                        <p style='margin: 0; color: #6c757d;'>
                            {total_topics} topics, {total_subtopics} subtopics tracked
                        </p>
                    </div>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>💾 Data Storage</h4>
                        <p style='margin: 0; color: #6c757d;'>
                            Progress: {"✅" if os.path.exists(self.progress_file) else "📝"} | 
                            Roadmap: {"✅" if os.path.exists(self.csv_file.replace('.csv', '_roadmap.json')) else "📝"}
                        </p>
                    </div>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>🆕 New Features</h4>
                        <p style='margin: 0; color: #6c757d;'>
                            ➕ Add/🗑️ Remove | 📊 Enhanced Analytics
                        </p>
                    </div>
                </div>
            </div>
            """)
            
            return widgets.VBox([header, system_info, tabs])
        except Exception as e:
            logger.error(f"Error displaying full system: {e}")
            return widgets.HTML(f"<p>Error loading system: {e}</p>")

def create_rf_learning_system() -> widgets.Widget:
    """
    Create and initialize the RF learning roadmap system.
    
    Returns:
        widgets.Widget: Complete learning system interface
    """
    try:
        """
        print("🚀 Initializing Enhanced RF IC Design Learning System...")
        print("🆕 Loading new features: Remove functionality + Analytics overview...")
        """
        system = RFLearningRoadmapSystem()

        """
        print("✅ System Initialization Complete!")
        print("\n" + "="*70)
        print("🎯 LEARNING SYSTEM")
        print("="*70)
        print("🆕 NEW FEATURES ADDED:")
        print("  ✅ 🗑️ Remove Topic/Subtopic functionality")
        print("  ✅ 📊 Enhanced Analytics with roadmap progress overview")
        print("  ✅ 🔍 Detailed subtopic-level progress tracking")
        print("  ✅ 💡 Smart recommendations (Quick wins + Focus areas)")
        print("  ✅ 📚 Learning insights with notes/resources tracking")
        print()
        print("📋 COMPLETE FEATURES LIST:")
        print("  • 📈 Progress tracking with dual notes system")
        print("  • ➕ Add custom topics/subtopics with priority levels")
        print("  • 🗑️ Remove topics/subtopics (with data cleanup)")
        print("  • 📊 Comprehensive analytics dashboard")
        print("  • 🗺️ Roadmap progress overview integration")
        print("  • 💾 Persistent data storage & backup")
        print("  • 🔓 Manual enable override for troubleshooting")
        print()
        print("🎯 ANALYTICS DASHBOARD FEATURES:")
        print("  • 📍 Phase-by-phase progress breakdown")
        print("  • 🎯 Topic completion rates with priority analysis")
        print("  • 🔍 Subtopic-level status tracking")
        print("  • 💡 Smart recommendations (Quick wins + Critical focus)")
        print("  • 📝📚 Notes and resources tracking")
        print("  • 🏆 Learning insights and motivation")
        print()
        print("🗑️ REMOVE FUNCTIONALITY:")
        print("  • Remove Topic: Xóa topic + tất cả subtopics + progress data")
        print("  • Remove Subtopic: Xóa chỉ subtopic được chọn + progress data")
        print("  • Auto cleanup: Tự động cập nhật dropdown và lưu thay đổi")
        print("  • Data integrity: Đảm bảo consistency sau khi xóa")
        print()
        print("🚀 Ready to use with all enhanced features!")
        print("="*70)
        """
        
        return system.display_full_system()
    except Exception as e:
        logger.error(f"Error creating learning system: {e}")
        return widgets.HTML(f"""
        <div style='padding: 30px; text-align: center; background: #f8d7da; border: 2px solid #f5c6cb; 
                    border-radius: 10px; color: #721c24;'>
            <h2>⚠️ System Initialization Error</h2>
            <p>Error details: {e}</p>
            <p>Please check the logs and try again.</p>
        </div>
        """)

if __name__ == "__main__":
    try:
        learning_system = create_rf_learning_system()
        display(learning_system)
    except Exception as e:
        print(f"❌ Critical Error: Unable to start the learning system")
        print(f"Error details: {e}")
        logger.error(f"Critical startup error: {e}")
        error_display = widgets.HTML(f"""
        <div style='padding: 20px; background: #f8d7da; border-radius: 10px; color: #721c24;'>
            <h3>⚠️ System Error</h3>
            <p>The RF IC Design Learning Roadmap System encountered an error during startup.</p>
            <p><strong>Error:</strong> {e}</p>
            <p>Please restart the notebook kernel and try again.</p>
        </div>
        """)
        display(error_display)
