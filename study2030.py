import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import warnings
import json
from typing import Dict, List, Optional, Tuple, Any
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RFLearningRoadmapSystem:
    """
    A comprehensive RF IC Design Learning Roadmap System with progress tracking,
    milestone management, analytics, and export capabilities.
    
    This system provides a structured 30+ month learning path from fundamentals
    to advanced RF IC design mastery, with interactive progress tracking and
    detailed analytics.
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
        
        # Define color schemes for different phases
        self.phase_colors = {
            'Foundation': '#3498db',
            'Short-term': '#e74c3c', 
            'Mid-term': '#f39c12',
            'Long-term': '#27ae60',
            'Advanced': '#9b59b6'
        }
        
        # Performance optimization: Cache frequently accessed data
        self._roadmap_cache = None
        self._progress_cache = {}
        self._milestones_cache = {}
        
        # Initialize the comprehensive roadmap
        self.roadmap = self._create_comprehensive_roadmap()
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
        """Load all data from CSV files with error handling."""
        try:
            self._load_progress()
            self._load_milestones()
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            
    def _load_progress(self) -> None:
        """Load learning progress from CSV file."""
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
        Save progress to CSV file with error handling.
        
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
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        rows.append({
                            'Phase': phase_name,
                            'Topic': topic_name,
                            'Subtopic': subtopic,
                            'Status': progress_info['status'],
                            'Completion_Percent': progress_info['completion'],
                            'Notes': progress_info['notes'],
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
        Save milestones to CSV file with error handling.
        
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
            Dict[str, Any]: Progress information with resources field
        """
        key = f"{phase}|{topic}|{subtopic}"
        default_info = {
            'status': 'Not Started',
            'completion': 0,
            'notes': '',
            'resources': '',  # NEW: Resources field
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        progress_info = self.progress.get(key, default_info)
        
        # Ensure resources field exists (for backward compatibility)
        if 'resources' not in progress_info:
            progress_info['resources'] = ''
            
        return progress_info
    
    def set_progress_info(self, phase: str, topic: str, subtopic: str, 
                         status: str, completion: int, notes: str, resources: str = '') -> bool:
        """
        Set progress information for a specific item with resources.
        
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
                'resources': resources,  # NEW: Store resources
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self._save_progress()
        except Exception as e:
            logger.error(f"Error setting progress info: {e}")
            return False

        """
        Args:
            phase (str): Phase name
            topic (str): Topic name
            subtopic (str): Subtopic name
            status (str): Status value
            completion (int): Completion percentage
            notes (str): Learning notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{phase}|{topic}|{subtopic}"
            self.progress[key] = {
                'status': status,
                'completion': completion,
                'notes': notes,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self._save_progress()
        except Exception as e:
            logger.error(f"Error setting progress info: {e}")
            return False
    
    def create_progress_manager(self) -> widgets.Widget:
        """
        Create an optimized progress management interface with fixed notes input
        and dynamic topic/subtopic management.
        
        Returns:
            widgets.Widget: Complete progress manager interface
        """
        # Phase selection
        phase_dropdown = widgets.Dropdown(
            options=['-- Select Phase --'] + list(self.roadmap.keys()),
            value='-- Select Phase --',
            description='Phase:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        # Topic selection with add functionality
        topic_dropdown = widgets.Dropdown(
            options=['-- Select Topic --'],
            value='-- Select Topic --',
            description='Topic:',
            layout=widgets.Layout(width='400px'),
            style={'description_width': '80px'}
        )
        
        # Add new topic widgets
        new_topic_text = widgets.Text(
            placeholder='Nhập tên topic mới...',
            layout=widgets.Layout(width='250px'),
            style={'description_width': '0px'}
        )
        
        topic_weeks = widgets.IntText(
            value=4,
            description='Weeks:',
            layout=widgets.Layout(width='100px'),
            style={'description_width': '50px'}
        )
        
        topic_priority = widgets.Dropdown(
            options=['Critical', 'High', 'Medium', 'Low'],
            value='High',
            description='Priority:',
            layout=widgets.Layout(width='120px'),
            style={'description_width': '60px'}
        )
        
        add_topic_btn = widgets.Button(
            description='➕ Add Topic',
            button_style='info',
            layout=widgets.Layout(width='100px')
        )
        
        # Subtopic selection with add functionality  
        subtopic_dropdown = widgets.Dropdown(
            options=['-- Select Subtopic --'],
            value='-- Select Subtopic --',
            description='Subtopic:',
            layout=widgets.Layout(width='400px'),
            style={'description_width': '80px'}
        )
        
        # Add new subtopic widget
        new_subtopic_text = widgets.Text(
            placeholder='Nhập tên subtopic mới...',
            layout=widgets.Layout(width='300px'),
            style={'description_width': '0px'}
        )
        
        add_subtopic_btn = widgets.Button(
            description='➕ Add Subtopic',
            button_style='info', 
            layout=widgets.Layout(width='120px')
        )
        
        # Status and completion
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
        
        # MAIN NOTES area
        notes_area = widgets.Textarea(
            value='',
            placeholder='Chọn subtopic trước để thêm ghi chú học tập...',
            layout=widgets.Layout(width='600px', height='120px'),
            disabled=True
        )
        
        # NEW: RESOURCES/DOCUMENTS notes area
        resources_area = widgets.Textarea(
            value='',
            placeholder='Nhập tên tài liệu, đường dẫn, links...',
            layout=widgets.Layout(width='600px', height='80px'),
            disabled=True
        )
        
        # Add a manual enable button for debugging
        enable_notes_btn = widgets.Button(
            description='🔓 Enable Notes',
            button_style='warning',
            layout=widgets.Layout(width='130px'),
            tooltip='Click to manually enable notes if auto-enable fails'
        )
        
        def force_enable_notes(b):
            """Force enable notes area - manual override."""
            notes_area.disabled = False
            resources_area.disabled = False
            notes_area.placeholder = 'Notes area manually enabled - you can type now!'
            resources_area.placeholder = 'Resources area manually enabled - add your documents/links!'
            enable_notes_btn.description = '✅ Notes Enabled'
            enable_notes_btn.button_style = 'success'
            enable_notes_btn.disabled = True
            status_indicator.value = "<div style='color: #28a745; padding: 5px;'>🔓 Both notes areas manually enabled</div>"
        
        enable_notes_btn.on_click(force_enable_notes)
        
        # Save button with loading state
        save_btn = widgets.Button(
            description='💾 Save Progress',
            button_style='success',
            layout=widgets.Layout(width='140px'),
            tooltip='Save your progress and notes'
        )
        
        # Current selection info
        selection_info = widgets.HTML(
            value="<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Chọn subtopic để bắt đầu track progress...</i></div>"
        )
        
        # Status indicator
        status_indicator = widgets.HTML()
        
        def add_new_topic(b):
            """Add new topic to selected phase."""
            selected_phase = phase_dropdown.value
            new_topic_name = new_topic_text.value.strip()
            
            if selected_phase == '-- Select Phase --':
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Phase trước khi thêm Topic</div>"
                return
                
            if not new_topic_name:
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Nhập tên Topic</div>"
                return
            
            try:
                # Add to roadmap structure
                if selected_phase not in self.roadmap:
                    status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>❌ Phase không tồn tại</div>"
                    return
                
                # Check if topic already exists
                if new_topic_name in self.roadmap[selected_phase]['topics']:
                    status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Topic '{new_topic_name}' đã tồn tại</div>"
                    return
                
                # Add new topic
                self.roadmap[selected_phase]['topics'][new_topic_name] = {
                    'weeks': topic_weeks.value,
                    'priority': topic_priority.value,
                    'subtopics': []  # Start empty, user can add subtopics
                }
                
                # Update dropdown options
                topics = list(self.roadmap[selected_phase]['topics'].keys())
                topic_dropdown.options = ['-- Select Topic --'] + topics
                topic_dropdown.value = new_topic_name  # Auto-select new topic
                
                # Clear input
                new_topic_text.value = ''
                
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã thêm Topic: {new_topic_name}</div>"
                
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi thêm topic: {e}</div>"
                logger.error(f"Error adding topic: {e}")
        
        def add_new_subtopic(b):
            """Add new subtopic to selected topic."""
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            new_subtopic_name = new_subtopic_text.value.strip()
            
            if selected_topic == '-- Select Topic --':
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn Topic trước khi thêm Subtopic</div>"
                return
                
            if not new_subtopic_name:
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Nhập tên Subtopic</div>"
                return
            
            try:
                # Check if subtopic already exists
                current_subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                if new_subtopic_name in current_subtopics:
                    status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Subtopic '{new_subtopic_name}' đã tồn tại</div>"
                    return
                
                # Add new subtopic
                self.roadmap[selected_phase]['topics'][selected_topic]['subtopics'].append(new_subtopic_name)
                
                # Update dropdown options
                subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
                subtopic_dropdown.value = new_subtopic_name  # Auto-select new subtopic
                
                # Clear input
                new_subtopic_text.value = ''
                
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã thêm Subtopic: {new_subtopic_name}</div>"
                
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi thêm subtopic: {e}</div>"
                logger.error(f"Error adding subtopic: {e}")
        
        add_topic_btn.on_click(add_new_topic)
        add_subtopic_btn.on_click(add_new_subtopic)
        
        def update_topic_options(change):
            """Update topic dropdown options based on selected phase."""
            selected_phase = change['new']
            if selected_phase == '-- Select Phase --':
                topic_dropdown.options = ['-- Select Topic --']
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            
            try:
                topics = list(self.roadmap[selected_phase]['topics'].keys())
                topic_dropdown.options = ['-- Select Topic --'] + topics
                topic_dropdown.value = '-- Select Topic --'
            except Exception as e:
                logger.error(f"Error updating topic options: {e}")
        
        def update_subtopic_options(change):
            """Update subtopic dropdown options based on selected topic."""
            selected_phase = phase_dropdown.value
            selected_topic = change['new']
            
            if (selected_topic == '-- Select Topic --' or 
                selected_phase == '-- Select Phase --'):
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            
            try:
                subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
                subtopic_dropdown.value = '-- Select Subtopic --'
            except Exception as e:
                logger.error(f"Error updating subtopic options: {e}")
        
        def update_progress_fields(change=None):
            """Update progress fields - SIMPLIFIED VERSION to fix notes issue."""
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            # Clear status first
            status_indicator.value = ""
            
            if (selected_subtopic == '-- Select Subtopic --' or
                selected_topic == '-- Select Topic --' or
                selected_phase == '-- Select Phase --'):
                
                # DISABLE notes areas
                notes_area.disabled = True
                resources_area.disabled = True
                notes_area.value = ''
                resources_area.value = ''
                notes_area.placeholder = 'Chọn Phase → Topic → Subtopic để kích hoạt notes...'
                resources_area.placeholder = 'Chọn subtopic để thêm tài liệu...'
                
                # Reset enable button
                enable_notes_btn.disabled = False
                enable_notes_btn.description = '🔓 Enable Notes'
                enable_notes_btn.button_style = 'warning'
                
                selection_info.value = "<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Chọn subtopic để bắt đầu track progress...</i></div>"
                return
            
            # All selections are valid - proceed
            try:
                # Load existing progress
                progress_info = self.get_progress_info(selected_phase, selected_topic, selected_subtopic)
                
                # Update other fields first
                status_dropdown.unobserve_all()  # Temporarily remove observers
                completion_slider.unobserve_all()
                
                status_dropdown.value = progress_info['status']
                completion_slider.value = progress_info['completion']
                
                # FORCE ENABLE both notes areas
                notes_area.disabled = False
                resources_area.disabled = False
                notes_area.value = progress_info['notes']
                notes_area.placeholder = f'Nhập ghi chú học tập cho "{selected_subtopic}"...'
                
                # Load resources from notes or separate field if available
                resources_info = progress_info.get('resources', '')  # New field for resources
                resources_area.value = resources_info
                resources_area.placeholder = f'Tài liệu/Links cho "{selected_subtopic}":\n• PDF: filename.pdf\n• Video: https://youtube.com/...\n• Book: Chapter 5, Page 123'
                
                # Update enable button state
                enable_notes_btn.description = '✅ Auto Enabled'
                enable_notes_btn.button_style = 'success' 
                enable_notes_btn.disabled = True
                
                # Update selection info
                topic_weeks = self.roadmap[selected_phase]['topics'][selected_topic]['weeks']
                priority = self.roadmap[selected_phase]['topics'][selected_topic]['priority']
                
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 
                                 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(priority, '#6c757d')
                
                selection_info.value = f"""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 8px; border-left: 4px solid {priority_color};'>
                    <h4 style='margin: 0 0 10px 0; color: #333;'>📖 Đã Chọn</h4>
                    <p style='margin: 0; color: #666;'><strong>Đường dẫn:</strong> {selected_phase.split(':')[0]} → {selected_topic} → {selected_subtopic}</p>
                    <p style='margin: 5px 0 0 0;'><span style='background: {priority_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em;'>{priority}</span> 
                    <strong>Thời gian:</strong> {topic_weeks} tuần | <strong>Cập nhật:</strong> {progress_info['last_updated']}</p>
                </div>
                """
                
                # Show success message
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã load dữ liệu cho: {selected_subtopic}</div>"
                
                logger.info(f"Successfully loaded progress for: {selected_subtopic}")
                
            except Exception as e:
                logger.error(f"Error in update_progress_fields: {e}")
                # Force enable notes anyway
                notes_area.disabled = False
                resources_area.disabled = False
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Lỗi load dữ liệu nhưng notes đã được kích hoạt</div>"
        
        def save_progress_info(b):
            """Save progress information with validation and feedback."""
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if (selected_subtopic == '-- Select Subtopic --' or
                selected_topic == '-- Select Topic --' or
                selected_phase == '-- Select Phase --'):
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Chọn subtopic trước</div>"
                return
            
            try:
                # Update button state
                save_btn.description = '💾 Saving...'
                save_btn.disabled = True
                
                # Get current values - FIXED: Direct access to widget values
                current_status = status_dropdown.value
                current_completion = completion_slider.value
                current_notes = notes_area.value
                current_resources = resources_area.value  # NEW: Save resources
                
                # Debug information
                logger.debug(f"Saving: Status={current_status}, Completion={current_completion}, Notes length={len(current_notes)}, Resources length={len(current_resources)}")
                
                # Enhanced progress info with resources
                key = f"{selected_phase}|{selected_topic}|{selected_subtopic}"
                self.progress[key] = {
                    'status': current_status,
                    'completion': current_completion,
                    'notes': current_notes,
                    'resources': current_resources,  # NEW: Store resources separately
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to file
                success = self._save_progress()
                
                if success:
                    status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã lưu progress cho: {selected_subtopic}</div>"
                    logger.info(f"Progress saved successfully for: {selected_subtopic}")
                    
                    # Show note preview if there are notes
                    if current_notes.strip():
                        note_preview = current_notes[:50] + "..." if len(current_notes) > 50 else current_notes
                        status_indicator.value += f"<div style='color: #6c757d; padding: 5px; font-style: italic; font-size: 0.9em;'>📝 Ghi chú: {note_preview}</div>"
                    
                    # Show resources preview if there are resources
                    if current_resources.strip():
                        resources_preview = current_resources[:50] + "..." if len(current_resources) > 50 else current_resources
                        status_indicator.value += f"<div style='color: #6c757d; padding: 5px; font-style: italic; font-size: 0.9em;'>📚 Tài liệu: {resources_preview}</div>"
                else:
                    status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>❌ Lỗi lưu progress</div>"
                    
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Lỗi: {str(e)}</div>"
                logger.error(f"Error in save_progress_info: {e}")
            finally:
                # Restore button state
                save_btn.description = '💾 Save Progress'
                save_btn.disabled = False
        
        # Set up event observers with error handling
        try:
            phase_dropdown.observe(update_topic_options, names='value')
            topic_dropdown.observe(update_subtopic_options, names='value')
            subtopic_dropdown.observe(update_progress_fields, names='value')
            save_btn.on_click(save_progress_info)
        except Exception as e:
            logger.error(f"Error setting up observers: {e}")
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📈 Learning Progress Manager</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Track your journey + Add custom topics/subtopics</p>
            </div>
            """),
            
            # Selection area with add functionality
            widgets.VBox([
                widgets.HTML("<h3 style='color: #2e7d32; margin-bottom: 15px;'>🎯 Select & Manage Learning Items</h3>"),
                
                # Phase selection
                phase_dropdown,
                widgets.HTML("<div style='height: 8px;'></div>"),
                
                # Topic selection + Add new topic
                widgets.HBox([
                    topic_dropdown,
                    widgets.HTML("<div style='width: 10px;'></div>"),
                    widgets.VBox([
                        widgets.HTML("<div style='font-size: 0.9em; color: #666; margin-bottom: 3px;'>Thêm Topic Mới:</div>"),
                        widgets.HBox([
                            new_topic_text,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            topic_weeks,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            topic_priority,
                            widgets.HTML("<div style='width: 5px;'></div>"),
                            add_topic_btn
                        ])
                    ])
                ], layout=widgets.Layout(align_items='flex-end')),
                
                widgets.HTML("<div style='height: 8px;'></div>"),
                
                # Subtopic selection + Add new subtopic
                widgets.HBox([
                    subtopic_dropdown,
                    widgets.HTML("<div style='width: 10px;'></div>"),
                    widgets.VBox([
                        widgets.HTML("<div style='font-size: 0.9em; color: #666; margin-bottom: 3px;'>Thêm Subtopic Mới:</div>"),
                        widgets.HBox([
                            new_subtopic_text,
                            widgets.HTML("<div style='width: 10px;'></div>"),
                            add_subtopic_btn
                        ])
                    ])
                ], layout=widgets.Layout(align_items='flex-end')),
                
                widgets.HTML("<div style='height: 10px;'></div>"),
                selection_info
            ], layout=widgets.Layout(
                border='2px solid #4CAF50', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#f8fffe'
            )),
            
            # Progress tracking area with dual notes
            widgets.VBox([
                widgets.HTML("<h3 style='color: #1976d2; margin-bottom: 15px;'>📊 Track Progress & Notes</h3>"),
                widgets.HBox([
                    status_dropdown, 
                    widgets.HTML("<div style='width: 20px;'></div>"),
                    completion_slider
                ], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 15px;'></div>"),
                
                # Learning Notes
                widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>📝 Learning Notes</h4>"),
                widgets.HTML("""
                <div style='background: #fff3cd; padding: 8px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 8px;'>
                    <strong>💡 Ghi chú học tập:</strong> Concepts, insights, questions, challenges...
                </div>
                """),
                notes_area,
                
                widgets.HTML("<div style='height: 15px;'></div>"),
                
                # Resources/Documents Notes  
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
                
                widgets.HBox([
                    save_btn,
                    widgets.HTML("<div style='width: 20px;'></div>"),
                    status_indicator
                ], layout=widgets.Layout(align_items='center')),
                
                # Usage examples
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("""
                <div style='background: #e8f4f8; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;'>
                    <strong>💡 Ví dụ sử dụng:</strong><br>
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
                </div>
                """)
            ], layout=widgets.Layout(
                border='2px solid #2196F3', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#f8fbff'
            ))
        ])
        """
        Create an optimized progress management interface with fixed notes input.
        
        Returns:
            widgets.Widget: Complete progress manager interface
        """
        # Phase selection
        phase_dropdown = widgets.Dropdown(
            options=['-- Select Phase --'] + list(self.roadmap.keys()),
            value='-- Select Phase --',
            description='Phase:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        # Topic selection
        topic_dropdown = widgets.Dropdown(
            options=['-- Select Topic --'],
            value='-- Select Topic --',
            description='Topic:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        # Subtopic selection
        subtopic_dropdown = widgets.Dropdown(
            options=['-- Select Subtopic --'],
            value='-- Select Subtopic --',
            description='Subtopic:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        # Status and completion
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
        
        # COMPLETELY FIXED notes area - using different approach
        notes_area = widgets.Textarea(
            value='',
            placeholder='Chọn subtopic trước để thêm ghi chú học tập...',
            layout=widgets.Layout(width='600px', height='150px'),
            disabled=True
        )
        
        # Add a manual enable button for debugging
        enable_notes_btn = widgets.Button(
            description='🔓 Enable Notes',
            button_style='warning',
            layout=widgets.Layout(width='130px'),
            tooltip='Click to manually enable notes if auto-enable fails'
        )
        
        def force_enable_notes(b):
            """Force enable notes area - manual override."""
            notes_area.disabled = False
            notes_area.placeholder = 'Notes area manually enabled - you can type now!'
            enable_notes_btn.description = '✅ Notes Enabled'
            enable_notes_btn.button_style = 'success'
            enable_notes_btn.disabled = True
            status_indicator.value = "<div style='color: #28a745; padding: 5px;'>🔓 Notes area manually enabled</div>"
        
        enable_notes_btn.on_click(force_enable_notes)
        
        # Save button with loading state
        save_btn = widgets.Button(
            description='💾 Save Progress',
            button_style='success',
            layout=widgets.Layout(width='140px'),
            tooltip='Save your progress and notes'
        )
        
        # Current selection info
        selection_info = widgets.HTML(
            value="<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Select a subtopic to track your progress...</i></div>"
        )
        
        # Status indicator
        status_indicator = widgets.HTML()
        
        def update_topic_options(change):
            """Update topic dropdown options based on selected phase."""
            selected_phase = change['new']
            if selected_phase == '-- Select Phase --':
                topic_dropdown.options = ['-- Select Topic --']
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            
            try:
                topics = list(self.roadmap[selected_phase]['topics'].keys())
                topic_dropdown.options = ['-- Select Topic --'] + topics
                topic_dropdown.value = '-- Select Topic --'
                logger.debug(f"Updated topics for phase: {selected_phase}")
            except Exception as e:
                logger.error(f"Error updating topic options: {e}")
        
        def update_subtopic_options(change):
            """Update subtopic dropdown options based on selected topic."""
            selected_phase = phase_dropdown.value
            selected_topic = change['new']
            
            if (selected_topic == '-- Select Topic --' or 
                selected_phase == '-- Select Phase --'):
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            
            try:
                subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
                subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
                subtopic_dropdown.value = '-- Select Subtopic --'
                logger.debug(f"Updated subtopics for topic: {selected_topic}")
            except Exception as e:
                logger.error(f"Error updating subtopic options: {e}")
        
        def update_progress_fields(change=None):
            """Update progress fields - SIMPLIFIED VERSION to fix notes issue."""
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            # Clear status first
            status_indicator.value = ""
            
            if (selected_subtopic == '-- Select Subtopic --' or
                selected_topic == '-- Select Topic --' or
                selected_phase == '-- Select Phase --'):
                
                # DISABLE notes area
                notes_area.disabled = True
                notes_area.value = ''
                notes_area.placeholder = 'Chọn Phase → Topic → Subtopic để kích hoạt notes...'
                
                # Reset enable button
                enable_notes_btn.disabled = False
                enable_notes_btn.description = '🔓 Enable Notes'
                enable_notes_btn.button_style = 'warning'
                
                selection_info.value = "<div style='padding: 10px; background: #f8f9fa; border-radius: 5px;'><i>📝 Chọn subtopic để bắt đầu track progress...</i></div>"
                return
            
            # All selections are valid - proceed
            try:
                # Load existing progress
                progress_info = self.get_progress_info(selected_phase, selected_topic, selected_subtopic)
                
                # Update other fields first
                status_dropdown.unobserve_all()  # Temporarily remove observers
                completion_slider.unobserve_all()
                
                status_dropdown.value = progress_info['status']
                completion_slider.value = progress_info['completion']
                
                # Re-attach observers
                # (Will be reattached at the end of function)
                
                # FORCE ENABLE notes area - this is the key fix
                notes_area.disabled = False
                notes_area.value = progress_info['notes']
                notes_area.placeholder = f'Nhập ghi chú học tập cho "{selected_subtopic}"...'
                
                # Update enable button state
                enable_notes_btn.description = '✅ Auto Enabled'
                enable_notes_btn.button_style = 'success' 
                enable_notes_btn.disabled = True
                
                # Update selection info
                topic_weeks = self.roadmap[selected_phase]['topics'][selected_topic]['weeks']
                priority = self.roadmap[selected_phase]['topics'][selected_topic]['priority']
                
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 
                                 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(priority, '#6c757d')
                
                selection_info.value = f"""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 8px; border-left: 4px solid {priority_color};'>
                    <h4 style='margin: 0 0 10px 0; color: #333;'>📖 Đã Chọn</h4>
                    <p style='margin: 0; color: #666;'><strong>Đường dẫn:</strong> {selected_phase.split(':')[0]} → {selected_topic} → {selected_subtopic}</p>
                    <p style='margin: 5px 0 0 0;'><span style='background: {priority_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em;'>{priority}</span> 
                    <strong>Thời gian:</strong> {topic_weeks} tuần | <strong>Cập nhật:</strong> {progress_info['last_updated']}</p>
                </div>
                """
                
                # Show success message
                status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Đã load dữ liệu cho: {selected_subtopic}</div>"
                
                logger.info(f"Successfully loaded progress for: {selected_subtopic}")
                
            except Exception as e:
                logger.error(f"Error in update_progress_fields: {e}")
                # Force enable notes anyway
                notes_area.disabled = False
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>⚠️ Lỗi load dữ liệu nhưng notes đã được kích hoạt</div>"
        
        def save_progress_info(b):
            """Save progress information with validation and feedback."""
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if (selected_subtopic == '-- Select Subtopic --' or
                selected_topic == '-- Select Topic --' or
                selected_phase == '-- Select Phase --'):
                status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ Please select a subtopic first</div>"
                return
            
            try:
                # Update button state
                save_btn.description = '💾 Saving...'
                save_btn.disabled = True
                
                # Get current values - FIXED: Direct access to widget values
                current_status = status_dropdown.value
                current_completion = completion_slider.value
                current_notes = notes_area.value  # This should work now
                
                # Debug information
                logger.debug(f"Saving: Status={current_status}, Completion={current_completion}, Notes length={len(current_notes)}")
                
                # Save progress with explicit values
                success = self.set_progress_info(
                    selected_phase, selected_topic, selected_subtopic,
                    current_status, current_completion, current_notes
                )
                
                if success:
                    status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Progress saved for: {selected_subtopic}</div>"
                    logger.info(f"Progress saved successfully for: {selected_subtopic}")
                    
                    # Show note preview if there are notes
                    if current_notes.strip():
                        note_preview = current_notes[:100] + "..." if len(current_notes) > 100 else current_notes
                        status_indicator.value += f"<div style='color: #6c757d; padding: 5px; font-style: italic; font-size: 0.9em;'>📝 Note saved: {note_preview}</div>"
                else:
                    status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>❌ Error saving progress</div>"
                    
            except Exception as e:
                status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Error: {str(e)}</div>"
                logger.error(f"Error in save_progress_info: {e}")
            finally:
                # Restore button state
                save_btn.description = '💾 Save Progress'
                save_btn.disabled = False
        
        # Set up event observers with error handling
        try:
            phase_dropdown.observe(update_topic_options, names='value')
            topic_dropdown.observe(update_subtopic_options, names='value')
            subtopic_dropdown.observe(update_progress_fields, names='value')
            save_btn.on_click(save_progress_info)
        except Exception as e:
            logger.error(f"Error setting up observers: {e}")
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📈 Learning Progress Manager</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Track your journey through RF IC design mastery</p>
            </div>
            """),
            
            # Selection area
            widgets.VBox([
                widgets.HTML("<h3 style='color: #2e7d32; margin-bottom: 15px;'>🎯 Select Learning Item</h3>"),
                phase_dropdown,
                widgets.HTML("<div style='height: 5px;'></div>"),
                topic_dropdown,
                widgets.HTML("<div style='height: 5px;'></div>"),
                subtopic_dropdown,
                widgets.HTML("<div style='height: 10px;'></div>"),
                selection_info
            ], layout=widgets.Layout(
                border='2px solid #4CAF50', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#f8fffe'
            )),
            
            # Progress tracking area
            widgets.VBox([
                widgets.HTML("<h3 style='color: #1976d2; margin-bottom: 15px;'>📊 Track Progress</h3>"),
                widgets.HBox([
                    status_dropdown, 
                    widgets.HTML("<div style='width: 20px;'></div>"),
                    completion_slider
                ], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>📝 Learning Notes</h4>"),
                widgets.HTML("""
                <div style='background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 10px;'>
                    <strong>🔧 Nếu không nhập được notes:</strong><br>
                    1. Chọn đầy đủ: Phase → Topic → Subtopic<br>
                    2. Nếu vẫn bị disabled (màu xám), click nút "🔓 Enable Notes" bên dưới<br>
                    3. Background sẽ chuyển sang trắng khi đã enable thành công
                </div>
                """),
                notes_area,
                widgets.HTML("<div style='height: 8px;'></div>"),
                widgets.HBox([
                    enable_notes_btn,
                    widgets.HTML("<div style='width: 15px;'></div>"),
                    widgets.HTML("<span style='color: #666; font-size: 0.9em; font-style: italic;'>👆 Click nếu notes area bị disabled</span>")
                ], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 10px;'></div>"),
                widgets.HBox([
                    save_btn,
                    widgets.HTML("<div style='width: 20px;'></div>"),
                    status_indicator
                ], layout=widgets.Layout(align_items='center')),
                
                # Debug panel for troubleshooting
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HTML("""
                <div style='background: #e8f4f8; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;'>
                    <strong>🔍 Debug Panel:</strong><br>
                    <span style='font-size: 0.9em; color: #666;'>
                    • Notes area disabled = màu xám, không type được<br>
                    • Notes area enabled = màu trắng, có thể type<br>
                    • Nếu auto-enable không hoạt động → dùng nút "🔓 Enable Notes"<br>
                    • Sau khi enable, hãy thử type vài từ để test
                    </span>
                </div>
                """)
            ], layout=widgets.Layout(
                border='2px solid #2196F3', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#f8fbff'
            ))
        ])
    
    def create_milestone_manager(self) -> widgets.Widget:
        """
        Create milestone management interface with enhanced functionality.
        
        Returns:
            widgets.Widget: Complete milestone manager interface
        """
        # Phase selection for milestones
        milestone_phase_dropdown = widgets.Dropdown(
            options=list(self.roadmap.keys()),
            description='Phase:',
            layout=widgets.Layout(width='450px'),
            style={'description_width': '80px'}
        )
        
        # Date pickers with better defaults
        start_date = widgets.DatePicker(
            description='Start Date:',
            value=datetime.now().date(),
            layout=widgets.Layout(width='220px'),
            style={'description_width': '80px'}
        )
        
        end_date = widgets.DatePicker(
            description='Target End:',
            value=(datetime.now() + timedelta(weeks=12)).date(),
            layout=widgets.Layout(width='220px'),
            style={'description_width': '80px'}
        )
        
        milestone_status = widgets.Dropdown(
            options=['Planned', 'Active', 'Completed', 'Delayed'],
            value='Planned',
            description='Status:',
            layout=widgets.Layout(width='180px'),
            style={'description_width': '60px'}
        )
        
        # Buttons
        set_milestone_btn = widgets.Button(
            description='🎯 Set Milestone',
            button_style='primary',
            layout=widgets.Layout(width='140px'),
            tooltip='Create or update milestone'
        )
        
        # Milestone display with enhanced styling
        milestone_display = widgets.HTML()
        milestone_status_indicator = widgets.HTML()
        
        def update_milestone_display():
            """Update milestone display with enhanced visualization."""
            if not self.milestones:
                milestone_display.value = """
                <div style='text-align: center; padding: 30px; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dee2e6;'>
                    <h4 style='color: #6c757d; margin-bottom: 10px;'>📅 No Milestones Set</h4>
                    <p style='color: #868e96; margin: 0;'>Create your first milestone to start tracking your learning timeline</p>
                </div>
                """
                return
            
            html_content = "<h4 style='color: #495057; margin-bottom: 15px;'>📅 Current Milestones</h4>"
            html_content += "<div style='max-height: 400px; overflow-y: auto; padding-right: 10px;'>"
            
            # Sort milestones by start date
            sorted_milestones = sorted(
                self.milestones.items(), 
                key=lambda x: x[1]['start_date']
            )
            
            for phase, info in sorted_milestones:
                status_colors = {
                    'Planned': '#ffc107', 
                    'Active': '#17a2b8', 
                    'Completed': '#28a745', 
                    'Delayed': '#dc3545'
                }
                status_color = status_colors.get(info['status'], '#6c757d')
                
                # Calculate progress indicators
                try:
                    start_dt = datetime.strptime(info['start_date'], '%Y-%m-%d')
                    end_dt = datetime.strptime(info['target_end_date'], '%Y-%m-%d')
                    total_days = (end_dt - start_dt).days
                    
                    if info['status'] == 'Active':
                        days_passed = (datetime.now() - start_dt).days
                        progress_percent = min(100, max(0, (days_passed / total_days) * 100))
                        progress_bar = f"""
                        <div style='width: 100%; background: #e9ecef; border-radius: 10px; margin: 8px 0;'>
                            <div style='width: {progress_percent}%; background: {status_color}; height: 6px; border-radius: 10px; transition: width 0.3s;'></div>
                        </div>
                        <small style='color: #6c757d;'>Progress: {progress_percent:.1f}% ({days_passed}/{total_days} days)</small>
                        """
                    else:
                        progress_bar = ""
                        
                except:
                    progress_bar = ""
                
                phase_short = phase.split(':')[0] if ':' in phase else phase
                
                html_content += f"""
                <div style='border: 2px solid {status_color}; border-radius: 12px; padding: 15px; margin: 10px 0; 
                            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248,249,250,0.9)); 
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s;'
                     onmouseover='this.style.transform="translateY(-2px)"' 
                     onmouseout='this.style.transform="translateY(0)"'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <h5 style='margin: 0; color: #333; font-size: 1.1em;'>{phase_short}</h5>
                        <span style='background: {status_color}; color: white; padding: 4px 12px; border-radius: 20px; 
                                   font-size: 0.85em; font-weight: bold;'>{info['status']}</span>
                    </div>
                    <div style='color: #666; font-size: 0.9em;'>
                        <div style='margin: 4px 0;'><strong>📅 Start:</strong> {info['start_date']}</div>
                        <div style='margin: 4px 0;'><strong>🎯 Target:</strong> {info['target_end_date']}</div>
                        {f"<div style='margin: 4px 0;'><strong>✅ Completed:</strong> {info['actual_end_date']}</div>" if info.get('actual_end_date') else ""}
                    </div>
                    {progress_bar}
                </div>
                """
            html_content += "</div>"
            milestone_display.value = html_content
        
        def set_milestone(b):
            """Set milestone with validation and feedback."""
            selected_phase = milestone_phase_dropdown.value
            
            try:
                # Validate dates
                if start_date.value >= end_date.value:
                    milestone_status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>⚠️ End date must be after start date</div>"
                    return
                
                # Update button state
                set_milestone_btn.description = '🎯 Setting...'
                set_milestone_btn.disabled = True
                
                # Set milestone
                self.milestones[selected_phase] = {
                    'start_date': start_date.value.strftime('%Y-%m-%d'),
                    'target_end_date': end_date.value.strftime('%Y-%m-%d'),
                    'actual_end_date': '',
                    'status': milestone_status.value
                }
                
                success = self._save_milestones()
                if success:
                    update_milestone_display()
                    milestone_status_indicator.value = f"<div style='color: #28a745; padding: 5px;'>✅ Milestone set for: {selected_phase.split(':')[0]}</div>"
                    logger.info(f"Milestone set successfully for: {selected_phase}")
                else:
                    milestone_status_indicator.value = "<div style='color: #dc3545; padding: 5px;'>❌ Error saving milestone</div>"
                    
            except Exception as e:
                milestone_status_indicator.value = f"<div style='color: #dc3545; padding: 5px;'>❌ Error: {str(e)}</div>"
                logger.error(f"Error setting milestone: {e}")
            finally:
                # Restore button state
                set_milestone_btn.description = '🎯 Set Milestone'
                set_milestone_btn.disabled = False
        
        # Auto-update end date based on phase duration
        def update_end_date_suggestion(change):
            """Auto-suggest end date based on phase duration."""
            selected_phase = change['new']
            if selected_phase in self.roadmap:
                duration_weeks = self.roadmap[selected_phase]['duration_weeks']
                suggested_end = start_date.value + timedelta(weeks=duration_weeks)
                end_date.value = suggested_end
        
        # Set up event handlers
        try:
            set_milestone_btn.on_click(set_milestone)
            milestone_phase_dropdown.observe(update_end_date_suggestion, names='value')
        except Exception as e:
            logger.error(f"Error setting up milestone manager observers: {e}")
        
        update_milestone_display()
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #FF9800, #F57C00); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>🎯 Milestone Manager</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Set and track your learning milestones</p>
            </div>
            """),
            
            widgets.VBox([
                widgets.HTML("<h3 style='color: #e65100; margin-bottom: 15px;'>📅 Create New Milestone</h3>"),
                milestone_phase_dropdown,
                widgets.HTML("<div style='height: 10px;'></div>"),
                widgets.HBox([
                    start_date, 
                    widgets.HTML("<div style='width: 15px;'></div>"),
                    end_date, 
                    widgets.HTML("<div style='width: 15px;'></div>"),
                    milestone_status
                ], layout=widgets.Layout(align_items='center')),
                widgets.HTML("<div style='height: 15px;'></div>"),
                widgets.HBox([
                    set_milestone_btn,
                    widgets.HTML("<div style='width: 20px;'></div>"),
                    milestone_status_indicator
                ], layout=widgets.Layout(align_items='center'))
            ], layout=widgets.Layout(
                border='2px solid #FF9800', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#fff8e1'
            )),
            
            milestone_display
        ])
    
    def create_analytics_dashboard(self) -> widgets.Widget:
        """
        Create comprehensive analytics and visualization dashboard.
        
        Returns:
            widgets.Widget: Complete analytics dashboard
        """
        analytics_output = widgets.Output()
        
        refresh_btn = widgets.Button(
            description='🔄 Refresh Analytics',
            button_style='info',
            layout=widgets.Layout(width='160px'),
            tooltip='Update all analytics and charts'
        )
        
        def generate_analytics(b=None):
            """Generate comprehensive analytics with error handling."""
            with analytics_output:
                clear_output(wait=True)
                
                try:
                    # Calculate overall progress statistics
                    total_items = 0
                    completed_items = 0
                    in_progress_items = 0
                    review_items = 0
                    
                    phase_stats = {}
                    priority_progress = {'Critical': {'total': 0, 'completed': 0},
                                       'High': {'total': 0, 'completed': 0},
                                       'Medium': {'total': 0, 'completed': 0},
                                       'Low': {'total': 0, 'completed': 0}}
                    
                    for phase_name, phase_data in self.roadmap.items():
                        phase_total = 0
                        phase_completed = 0
                        phase_in_progress = 0
                        phase_review = 0
                        
                        for topic_name, topic_data in phase_data['topics'].items():
                            priority = topic_data['priority']
                            for subtopic in topic_data['subtopics']:
                                total_items += 1
                                phase_total += 1
                                priority_progress[priority]['total'] += 1
                                
                                progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                                status = progress_info['status']
                                
                                if status == 'Completed':
                                    completed_items += 1
                                    phase_completed += 1
                                    priority_progress[priority]['completed'] += 1
                                elif status in ['In Progress']:
                                    in_progress_items += 1
                                    phase_in_progress += 1
                                elif status == 'Review':
                                    review_items += 1
                                    phase_review += 1
                        
                        completion_rate = (phase_completed / phase_total * 100) if phase_total > 0 else 0
                        phase_stats[phase_name] = {
                            'total': phase_total,
                            'completed': phase_completed,
                            'in_progress': phase_in_progress,
                            'review': phase_review,
                            'completion_rate': completion_rate
                        }
                    
                    # Create enhanced visualizations
                    fig = plt.figure(figsize=(16, 12))
                    fig.suptitle('RF IC Design Learning Analytics Dashboard', fontsize=18, fontweight='bold', y=0.95)
                    
                    # Create a 3x2 subplot layout
                    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1], hspace=0.3, wspace=0.3)
                    
                    # 1. Overall progress pie chart
                    ax1 = fig.add_subplot(gs[0, 0])
                    overall_not_started = total_items - completed_items - in_progress_items - review_items
                    sizes = [completed_items, in_progress_items, review_items, overall_not_started]
                    labels = ['Completed', 'In Progress', 'Review', 'Not Started']
                    colors = ['#28a745', '#ffc107', '#17a2b8', '#dc3545']
                    
                    # Only show non-zero slices
                    non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
                    if non_zero_data:
                        sizes_nz, labels_nz, colors_nz = zip(*non_zero_data)
                        wedges, texts, autotexts = ax1.pie(sizes_nz, labels=labels_nz, colors=colors_nz,
                                                          autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total_items)})',
                                                          startangle=90, textprops={'fontsize': 9})
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                    
                    ax1.set_title('Overall Progress Distribution', fontsize=12, fontweight='bold', pad=20)
                    
                    # 2. Progress by phase bar chart
                    ax2 = fig.add_subplot(gs[0, 1])
                    phases = list(phase_stats.keys())
                    completion_rates = [phase_stats[phase]['completion_rate'] for phase in phases]
                    phase_colors_list = [self.phase_colors.get(self.roadmap[phase]['phase'], '#6c757d') for phase in phases]
                    
                    bars = ax2.bar(range(len(phases)), completion_rates, color=phase_colors_list, alpha=0.8, edgecolor='black', linewidth=0.5)
                    ax2.set_xlabel('Learning Phases', fontweight='bold')
                    ax2.set_ylabel('Completion Rate (%)', fontweight='bold')
                    ax2.set_title('Progress by Phase', fontsize=12, fontweight='bold', pad=20)
                    ax2.set_xticks(range(len(phases)))
                    ax2.set_xticklabels([phase.split(':')[0] for phase in phases], rotation=45, ha='right', fontsize=9)
                    ax2.set_ylim(0, 105)
                    ax2.grid(True, alpha=0.3, axis='y')
                    
                    # Add value labels on bars
                    for bar, rate in zip(bars, completion_rates):
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
                    
                    # 3. Priority-based progress
                    ax3 = fig.add_subplot(gs[1, 0])
                    priorities = list(priority_progress.keys())
                    priority_completion_rates = []
                    for priority in priorities:
                        total_p = priority_progress[priority]['total']
                        completed_p = priority_progress[priority]['completed']
                        rate = (completed_p / total_p * 100) if total_p > 0 else 0
                        priority_completion_rates.append(rate)
                    
                    priority_colors_map = {'Critical': '#dc3545', 'High': '#fd7e14', 
                                         'Medium': '#ffc107', 'Low': '#28a745'}
                    colors_p = [priority_colors_map[p] for p in priorities]
                    
                    bars_p = ax3.bar(priorities, priority_completion_rates, color=colors_p, alpha=0.8, edgecolor='black', linewidth=0.5)
                    ax3.set_xlabel('Priority Level', fontweight='bold')
                    ax3.set_ylabel('Completion Rate (%)', fontweight='bold')
                    ax3.set_title('Progress by Priority', fontsize=12, fontweight='bold', pad=20)
                    ax3.set_ylim(0, 105)
                    ax3.grid(True, alpha=0.3, axis='y')
                    
                    # Add value labels and item counts
                    for bar, priority in zip(bars_p, priorities):
                        height = bar.get_height()
                        total_items_p = priority_progress[priority]['total']
                        completed_items_p = priority_progress[priority]['completed']
                        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
                        ax3.text(bar.get_x() + bar.get_width()/2., height/2,
                                f'{completed_items_p}/{total_items_p}', ha='center', va='center', 
                                color='white', fontweight='bold', fontsize=8)
                    
                    # 4. Timeline view (enhanced)
                    ax4 = fig.add_subplot(gs[1, 1])
                    if self.milestones:
                        milestone_phases = []
                        start_dates = []
                        end_dates = []
                        statuses = []
                        
                        for phase, info in self.milestones.items():
                            if info['start_date'] and info['target_end_date']:
                                milestone_phases.append(phase.split(':')[0])
                                start_dates.append(pd.to_datetime(info['start_date']))
                                end_dates.append(pd.to_datetime(info['target_end_date']))
                                statuses.append(info['status'])
                        
                        if milestone_phases:
                            y_pos = np.arange(len(milestone_phases))
                            durations = [(end - start).days for start, end in zip(start_dates, end_dates)]
                            
                            # Color by status
                            status_colors_timeline = {'Planned': '#ffc107', 'Active': '#17a2b8', 
                                                    'Completed': '#28a745', 'Delayed': '#dc3545'}
                            bar_colors = [status_colors_timeline.get(status, '#6c757d') for status in statuses]
                            
                            bars_t = ax4.barh(y_pos, durations, left=[d.toordinal() for d in start_dates], 
                                            color=bar_colors, alpha=0.8, edgecolor='black', linewidth=0.5)
                            ax4.set_yticks(y_pos)
                            ax4.set_yticklabels(milestone_phases, fontsize=9)
                            ax4.set_xlabel('Timeline', fontweight='bold')
                            ax4.set_title('Learning Phase Timeline', fontsize=12, fontweight='bold', pad=20)
                            
                            # Format x-axis as dates
                            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                            ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
                            ax4.grid(True, alpha=0.3, axis='x')
                            
                            # Add status labels
                            for i, (bar, status, duration) in enumerate(zip(bars_t, statuses, durations)):
                                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                                        f'{status}\n{duration}d', ha='center', va='center',
                                        color='white', fontweight='bold', fontsize=7)
                    else:
                        ax4.text(0.5, 0.5, '📅 Set milestones to view timeline\n\nUse the Milestone Manager tab\nto create your learning timeline', 
                                ha='center', va='center', transform=ax4.transAxes,
                                fontsize=11, style='italic', bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor='lightgray', alpha=0.5))
                        ax4.set_title('Learning Phase Timeline', fontsize=12, fontweight='bold', pad=20)
                    
                    # 5. Learning velocity (items completed over time)
                    ax5 = fig.add_subplot(gs[2, :])
                    
                    # Extract completion dates and create velocity chart
                    completion_dates = []
                    for progress_info in self.progress.values():
                        if progress_info['status'] == 'Completed' and progress_info['last_updated']:
                            try:
                                date = datetime.strptime(progress_info['last_updated'], '%Y-%m-%d %H:%M:%S').date()
                                completion_dates.append(date)
                            except:
                                pass
                    
                    if completion_dates:
                        completion_dates.sort()
                        
                        # Create cumulative completion chart
                        date_counts = {}
                        for date in completion_dates:
                            date_counts[date] = date_counts.get(date, 0) + 1
                        
                        dates = list(date_counts.keys())
                        cumulative_counts = []
                        running_total = 0
                        for date in dates:
                            running_total += date_counts[date]
                            cumulative_counts.append(running_total)
                        
                        ax5.plot(dates, cumulative_counts, marker='o', linewidth=2, markersize=6, 
                                color='#2196F3', markerfacecolor='#1976D2', markeredgecolor='white')
                        ax5.fill_between(dates, cumulative_counts, alpha=0.3, color='#2196F3')
                        
                        ax5.set_xlabel('Date', fontweight='bold')
                        ax5.set_ylabel('Cumulative Items Completed', fontweight='bold')
                        ax5.set_title('Learning Velocity - Cumulative Progress Over Time', fontsize=12, fontweight='bold', pad=20)
                        ax5.grid(True, alpha=0.3)
                        
                        # Format dates on x-axis
                        ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                        ax5.xaxis.set_major_locator(mdates.MonthLocator())
                        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
                        
                        # Add trend line
                        if len(dates) > 1:
                            x_numeric = [d.toordinal() for d in dates]
                            z = np.polyfit(x_numeric, cumulative_counts, 1)
                            p = np.poly1d(z)
                            ax5.plot(dates, p([d.toordinal() for d in dates]), "--", 
                                    color='red', alpha=0.8, linewidth=2, label=f'Trend (slope: {z[0]:.2f} items/day)')
                            ax5.legend()
                    else:
                        ax5.text(0.5, 0.5, '📈 Complete some items to view\nyour learning velocity!\n\nThis chart will show your progress over time', 
                                ha='center', va='center', transform=ax5.transAxes,
                                fontsize=11, style='italic', bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor='lightblue', alpha=0.3))
                        ax5.set_title('Learning Velocity - Cumulative Progress Over Time', fontsize=12, fontweight='bold', pad=20)
                    
                    plt.tight_layout()
                    plt.subplots_adjust(top=0.92)
                    plt.show()
                    
                    # Display enhanced summary statistics
                    print("\n" + "="*70)
                    print("📊 RF IC DESIGN LEARNING ANALYTICS DASHBOARD")
                    print("="*70)
                    
                    overall_completion = (completed_items/total_items*100) if total_items > 0 else 0
                    print(f"📈 Overall Progress: {completed_items}/{total_items} completed ({overall_completion:.1f}%)")
                    print(f"🔄 Currently In Progress: {in_progress_items} items")
                    print(f"📋 In Review: {review_items} items")
                    print(f"⏳ Not Started: {total_items - completed_items - in_progress_items - review_items} items")
                    
                    print(f"\n📋 Progress by Phase:")
                    for phase, stats in phase_stats.items():
                        phase_short = phase.split(':')[0]
                        print(f"  • {phase_short}: {stats['completed']}/{stats['total']} ({stats['completion_rate']:.1f}%) "
                              f"[{stats['in_progress']} in progress, {stats['review']} in review]")
                    
                    print(f"\n🎯 Progress by Priority:")
                    for priority in ['Critical', 'High', 'Medium', 'Low']:
                        total_p = priority_progress[priority]['total']
                        completed_p = priority_progress[priority]['completed']
                        rate_p = (completed_p / total_p * 100) if total_p > 0 else 0
                        print(f"  • {priority}: {completed_p}/{total_p} ({rate_p:.1f}%)")
                    
                    # Enhanced recommendations
                    print(f"\n🎯 PERSONALIZED RECOMMENDATIONS:")
                    recommendations = self._get_learning_recommendations()
                    for i, rec in enumerate(recommendations[:7], 1):
                        print(f"  {i}. {rec}")
                    
                    # Learning insights
                    print(f"\n💡 LEARNING INSIGHTS:")
                    insights = self._generate_learning_insights(phase_stats, priority_progress, overall_completion)
                    for insight in insights:
                        print(f"  • {insight}")
                        
                except Exception as e:
                    print(f"❌ Error generating analytics: {e}")
                    logger.error(f"Analytics generation error: {e}")
        
        refresh_btn.on_click(generate_analytics)
        generate_analytics()  # Initial load
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #6a11cb, #2575fc); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📊 Learning Analytics Dashboard</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Comprehensive insights into your learning journey</p>
            </div>
            """),
            
            widgets.HBox([
                refresh_btn,
                widgets.HTML("<div style='width: 20px;'></div>"),
                widgets.HTML("<div style='color: #666; font-style: italic; padding: 8px 0;'>💡 Analytics update automatically when you track progress</div>")
            ], layout=widgets.Layout(margin='0 0 15px 0')),
            
            analytics_output
        ])
    
    def _get_learning_recommendations(self) -> List[str]:
        """
        Generate intelligent learning recommendations based on current progress.
        
        Returns:
            List[str]: List of personalized recommendations
        """
        recommendations = []
        
        try:
            # Check for critical items not started
            critical_not_started = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    if topic_data['priority'] == 'Critical':
                        for subtopic in topic_data['subtopics']:
                            progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                            if progress_info['status'] == 'Not Started':
                                critical_not_started.append((subtopic, topic_name, phase_name.split(':')[0]))
            
            if critical_not_started:
                item = critical_not_started[0]
                recommendations.append(f"🔥 Priority: Start critical topic '{item[0]}' in {item[1]} ({item[2]})")
            
            # Check for items in review status
            review_items = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    for subtopic in topic_data['subtopics']:
                        progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                        if progress_info['status'] == 'Review':
                            review_items.append(subtopic)
            
            if review_items:
                recommendations.append(f"📚 Complete reviews for: {', '.join(review_items[:3])}{'...' if len(review_items) > 3 else ''}")
            
            # Check for sequential phase progression
            phase_order = list(self.roadmap.keys())
            for i, phase_name in enumerate(phase_order[:-1]):
                next_phase = phase_order[i + 1]
                current_completion = self._calculate_phase_completion(phase_name)
                next_phase_started = self._has_phase_started(next_phase)
                
                if current_completion > 70 and not next_phase_started:
                    recommendations.append(f"🚀 Ready to advance: Consider starting '{next_phase.split(':')[0]}'")
                elif current_completion < 30 and next_phase_started:
                    recommendations.append(f"⚠️ Focus needed: Complete more of '{phase_name.split(':')[0]}' before advancing")
            
            # Check for incomplete high-priority items
            high_priority_incomplete = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    if topic_data['priority'] == 'High':
                        incomplete_count = 0
                        for subtopic in topic_data['subtopics']:
                            progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                            if progress_info['status'] not in ['Completed']:
                                incomplete_count += 1
                        if incomplete_count > 0:
                            high_priority_incomplete.append((topic_name, incomplete_count, phase_name.split(':')[0]))
            
            if high_priority_incomplete:
                topic_info = high_priority_incomplete[0]
                recommendations.append(f"⭐ High priority: Complete {topic_info[1]} items in '{topic_info[0]}' ({topic_info[2]})")
            
            # Learning velocity recommendations
            recent_activity = self._check_recent_activity()
            if not recent_activity:
                recommendations.append("📅 Stay consistent: No recent progress detected. Try to study regularly!")
            
            # Milestone-based recommendations
            if self.milestones:
                overdue_milestones = []
                for phase, info in self.milestones.items():
                    if info['status'] == 'Active':
                        try:
                            target_date = datetime.strptime(info['target_end_date'], '%Y-%m-%d').date()
                            if target_date < datetime.now().date():
                                overdue_milestones.append(phase.split(':')[0])
                        except:
                            pass
                
                if overdue_milestones:
                    recommendations.append(f"⏰ Milestone alert: {overdue_milestones[0]} is overdue - consider updating timeline")
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            
        return recommendations if recommendations else ["🎉 Excellent progress! Keep up the great work on your learning journey."]
    
    def _generate_learning_insights(self, phase_stats: Dict, priority_progress: Dict, overall_completion: float) -> List[str]:
        """
        Generate intelligent learning insights based on progress data.
        
        Args:
            phase_stats: Phase completion statistics
            priority_progress: Priority-based progress data
            overall_completion: Overall completion percentage
            
        Returns:
            List[str]: List of learning insights
        """
        insights = []
        
        try:
            # Overall progress insights
            if overall_completion > 75:
                insights.append("Outstanding progress! You're well on your way to RF IC design mastery.")
            elif overall_completion > 50:
                insights.append("Great momentum! You've completed over half of your learning journey.")
            elif overall_completion > 25:
                insights.append("Solid foundation being built. Keep maintaining consistent progress.")
            else:
                insights.append("Just getting started! Focus on building strong fundamentals first.")
            
            # Priority-based insights
            critical_completion = priority_progress['Critical']['completed'] / max(1, priority_progress['Critical']['total']) * 100
            if critical_completion < 50:
                insights.append("Focus on critical topics - they're essential for building strong foundations.")
            elif critical_completion > 80:
                insights.append("Excellent work on critical topics! This strong foundation will serve you well.")
            
            # Phase distribution insights
            active_phases = sum(1 for stats in phase_stats.values() if stats['completion_rate'] > 0 and stats['completion_rate'] < 100)
            if active_phases > 2:
                insights.append("Consider focusing on fewer phases simultaneously for better learning depth.")
            elif active_phases == 0:
                insights.append("Ready to start! Begin with Foundation phase for the best learning experience.")
            
            # Learning pattern insights
            total_in_progress = sum(stats['in_progress'] for stats in phase_stats.values())
            total_review = sum(stats['review'] for stats in phase_stats.values())
            
            if total_review > total_in_progress and total_review > 5:
                insights.append("Many items in review - consider scheduling regular review sessions to consolidate learning.")
            
            if total_in_progress > 15:
                insights.append("Many items in progress - try to complete some before starting new topics.")
                
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            
        return insights
    
    def _check_recent_activity(self) -> bool:
        """
        Check if there has been recent learning activity (within last 7 days).
        
        Returns:
            bool: True if there was recent activity, False otherwise
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for progress_info in self.progress.values():
                if progress_info['last_updated']:
                    try:
                        last_update = datetime.strptime(progress_info['last_updated'], '%Y-%m-%d %H:%M:%S')
                        if last_update > cutoff_date:
                            return True
                    except:
                        continue
            return False
        except:
            return True  # Assume activity if we can't determine
    
    def _calculate_phase_completion(self, phase_name: str) -> float:
        """
        Calculate completion percentage for a specific phase.
        
        Args:
            phase_name (str): Name of the phase
            
        Returns:
            float: Completion percentage (0-100)
        """
        if phase_name not in self.roadmap:
            return 0.0
        
        try:
            total_items = 0
            completed_items = 0
            
            for topic_data in self.roadmap[phase_name]['topics'].values():
                for subtopic in topic_data['subtopics']:
                    total_items += 1
                    progress_info = self.get_progress_info(phase_name, "", subtopic)
                    if progress_info['status'] == 'Completed':
                        completed_items += 1
            
            return (completed_items / total_items * 100) if total_items > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating phase completion: {e}")
            return 0.0
    
    def _has_phase_started(self, phase_name: str) -> bool:
        """
        Check if any item in a phase has been started.
        
        Args:
            phase_name (str): Name of the phase
            
        Returns:
            bool: True if phase has been started, False otherwise
        """
        if phase_name not in self.roadmap:
            return False
        
        try:
            for topic_data in self.roadmap[phase_name]['topics'].values():
                for subtopic in topic_data['subtopics']:
                    progress_info = self.get_progress_info(phase_name, "", subtopic)
                    if progress_info['status'] != 'Not Started':
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking if phase started: {e}")
            return False
    
    def create_roadmap_overview(self) -> widgets.Widget:
        """
        Create a comprehensive and visually appealing roadmap overview.
        
        Returns:
            widgets.Widget: Complete roadmap overview interface
        """
        # Enhanced header with statistics
        total_weeks = sum(phase_data['duration_weeks'] for phase_data in self.roadmap.values())
        total_topics = sum(len(phase_data['topics']) for phase_data in self.roadmap.values())
        total_subtopics = sum(
            len(topic_data['subtopics']) 
            for phase_data in self.roadmap.values() 
            for topic_data in phase_data['topics'].values()
        )
        
        overview_html = f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
            <h1 style='text-align: center; margin-bottom: 15px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🎯 RF IC Design Learning Roadmap</h1>
            <p style='text-align: center; font-size: 1.3em; margin-bottom: 20px; opacity: 0.95;'>Your comprehensive journey from fundamentals to mastery</p>
            
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 20px;'>
                <div style='text-align: center; margin: 10px;'>
                    <div style='font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{total_weeks}</div>
                    <div style='opacity: 0.9; font-size: 1.1em;'>Total Weeks</div>
                </div>
                <div style='text-align: center; margin: 10px;'>
                    <div style='font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{total_topics}</div>
                    <div style='opacity: 0.9; font-size: 1.1em;'>Major Topics</div>
                </div>
                <div style='text-align: center; margin: 10px;'>
                    <div style='font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{total_subtopics}</div>
                    <div style='opacity: 0.9; font-size: 1.1em;'>Learning Items</div>
                </div>
                <div style='text-align: center; margin: 10px;'>
                    <div style='font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>5</div>
                    <div style='opacity: 0.9; font-size: 1.1em;'>Learning Phases</div>
                </div>
            </div>
        </div>
        """
        
        # Create detailed roadmap display with enhanced styling
        roadmap_content = ""
        
        for i, (phase_name, phase_data) in enumerate(self.roadmap.items(), 1):
            color = self.phase_colors.get(phase_data['phase'], '#6c757d')
            phase_short = phase_name.split(':')[0] if ':' in phase_name else phase_name
            
            # Calculate phase progress
            phase_completion = self._calculate_phase_completion(phase_name)
            progress_bar = f"""
            <div style='width: 100%; background: rgba(255,255,255,0.3); border-radius: 10px; margin: 10px 0; height: 8px;'>
                <div style='width: {phase_completion}%; background: rgba(255,255,255,0.8); height: 8px; border-radius: 10px; transition: width 0.3s;'></div>
            </div>
            <div style='text-align: right; font-size: 0.9em; margin-top: 5px; opacity: 0.9;'>Progress: {phase_completion:.1f}%</div>
            """
            
            roadmap_content += f"""
            <div style='border: 3px solid {color}; border-radius: 15px; padding: 25px; margin: 20px 0; 
                        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95)); 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); transition: transform 0.3s;'
                 onmouseover='this.style.transform="translateY(-5px)"' 
                 onmouseout='this.style.transform="translateY(0)"'>
                
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                    <h2 style='color: {color}; margin: 0; font-size: 1.8em;'>Phase {i}: {phase_name}</h2>
                    <div style='background: {color}; color: white; padding: 8px 16px; border-radius: 25px; font-weight: bold; font-size: 0.9em;'>
                        {phase_data['duration_weeks']} weeks
                    </div>
                </div>
                
                <p style='font-style: italic; margin-bottom: 20px; color: #666; font-size: 1.1em; line-height: 1.5;'>{phase_data['description']}</p>
                {progress_bar}
                
                <div style='margin-top: 25px;'>
            """
            
            for j, (topic_name, topic_data) in enumerate(phase_data['topics'].items(), 1):
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(topic_data['priority'], '#6c757d')
                
                # Calculate topic progress
                topic_completed = 0
                topic_total = len(topic_data['subtopics'])
                for subtopic in topic_data['subtopics']:
                    progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                    if progress_info['status'] == 'Completed':
                        topic_completed += 1
                
                topic_progress = (topic_completed / topic_total * 100) if topic_total > 0 else 0
                
                roadmap_content += f"""
                    <div style='border-left: 5px solid {priority_color}; padding-left: 20px; margin: 20px 0; 
                                background: rgba(255,255,255,0.7); border-radius: 0 10px 10px 0; padding: 15px 15px 15px 20px;'>
                        
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                            <h4 style='color: #333; margin: 0; font-size: 1.3em;'>{j}.{topic_name}</h4>
                            <div style='display: flex; align-items: center; gap: 15px;'>
                                <span style='background: {priority_color}; color: white; padding: 4px 12px; border-radius: 20px; 
                                           font-size: 0.85em; font-weight: bold;'>{topic_data['priority']}</span>
                                <span style='color: #666; font-weight: bold;'>{topic_data['weeks']} weeks</span>
                            </div>
                        </div>
                        
                        <div style='margin: 12px 0;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                                <span style='font-size: 0.9em; color: #666;'>Topic Progress</span>
                                <span style='font-size: 0.9em; font-weight: bold; color: {priority_color};'>{topic_completed}/{topic_total} ({topic_progress:.0f}%)</span>
                            </div>
                            <div style='width: 100%; background: #e9ecef; border-radius: 10px; height: 6px;'>
                                <div style='width: {topic_progress}%; background: {priority_color}; height: 6px; border-radius: 10px; transition: width 0.3s;'></div>
                            </div>
                        </div>
                        
                        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; margin-top: 15px;'>
                """
                
                for k, subtopic in enumerate(topic_data['subtopics'], 1):
                    progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                    status = progress_info['status']
                    
                    status_colors = {
                        'Completed': '#28a745',
                        'In Progress': '#ffc107', 
                        'Review': '#17a2b8',
                        'Not Started': '#e9ecef',
                        'Skipped': '#6c757d'
                    }
                    status_color = status_colors.get(status, '#e9ecef')
                    text_color = 'white' if status != 'Not Started' else '#333'
                    
                    roadmap_content += f"""
                        <div style='background: {status_color}; color: {text_color}; padding: 8px 12px; border-radius: 8px; 
                                   font-size: 0.9em; display: flex; justify-content: space-between; align-items: center; 
                                   transition: transform 0.2s;' 
                             onmouseover='this.style.transform="scale(1.02)"' 
                             onmouseout='this.style.transform="scale(1)"'>
                            <span>{k}. {subtopic}</span>
                            <span style='font-size: 0.8em; opacity: 0.8;'>{status}</span>
                        </div>
                    """
                
                roadmap_content += "</div></div>"
            
            roadmap_content += "</div></div>"
        
        # Enhanced learning strategy section
        strategy_html = f"""
        <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 3px solid #28a745; border-radius: 15px; padding: 25px; margin: 25px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
            <h2 style='color: #28a745; text-align: center; margin-bottom: 25px; font-size: 2em;'>📋 Strategic Learning Framework</h2>
            
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 25px 0;'>
                <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-left: 5px solid {self.phase_colors["Foundation"]};'>
                    <h3 style='color: {self.phase_colors["Foundation"]}; text-align: center; margin-bottom: 15px;'>🏗️ Foundation Phase</h3>
                    <ul style='color: #555; line-height: 1.6;'>
                        <li><strong>Focus:</strong> Mathematical & circuit fundamentals</li>
                        <li><strong>Goal:</strong> Solid theoretical foundation</li>
                        <li><strong>Key Skills:</strong> Complex analysis, network theory</li>
                        <li><strong>Outcome:</strong> Ready for analog IC design</li>
                    </ul>
                </div>
                
                <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-left: 5px solid {self.phase_colors["Short-term"]};'>
                    <h3 style='color: {self.phase_colors["Short-term"]}; text-align: center; margin-bottom: 15px;'>🚀 Short-term Phase</h3>
                    <ul style='color: #555; line-height: 1.6;'>
                        <li><strong>Focus:</strong> Analog IC design mastery</li>
                        <li><strong>Goal:</strong> Design operational amplifiers</li>
                        <li><strong>Key Skills:</strong> OpAmp design, data converters</li>
                        <li><strong>Outcome:</strong> Competent analog designer</li>
                    </ul>
                </div>
                
                <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-left: 5px solid {self.phase_colors["Mid-term"]};'>
                    <h3 style='color: {self.phase_colors["Mid-term"]}; text-align: center; margin-bottom: 15px;'>⚡ Mid-term Phase</h3>
                    <ul style='color: #555; line-height: 1.6;'>
                        <li><strong>Focus:</strong> Advanced microwave & high-speed</li>
                        <li><strong>Goal:</strong> SerDes and microwave expertise</li>
                        <li><strong>Key Skills:</strong> EM simulation, signal integrity</li>
                        <li><strong>Outcome:</strong> High-speed design capability</li>
                    </ul>
                </div>
                
                <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-left: 5px solid {self.phase_colors["Long-term"]};'>
                    <h3 style='color: {self.phase_colors["Long-term"]}; text-align: center; margin-bottom: 15px;'>🏆 Long-term Phase</h3>
                    <ul style='color: #555; line-height: 1.6;'>
                        <li><strong>Focus:</strong> RF IC design mastery</li>
                        <li><strong>Goal:</strong> Complete RF transceiver design</li>
                        <li><strong>Key Skills:</strong> LNA, VCO, mixer design</li>
                        <li><strong>Outcome:</strong> RF system architect</li>
                    </ul>
                </div>
                
                <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-left: 5px solid {self.phase_colors["Advanced"]};'>
                    <h3 style='color: {self.phase_colors["Advanced"]}; text-align: center; margin-bottom: 15px;'>🌟 Advanced Phase</h3>
                    <ul style='color: #555; line-height: 1.6;'>
                        <li><strong>Focus:</strong> Cutting-edge applications</li>
                        <li><strong>Goal:</strong> Industry leadership</li>
                        <li><strong>Key Skills:</strong> mmWave, 5G, automotive radar</li>
                        <li><strong>Outcome:</strong> Technology innovator</li>
                    </ul>
                </div>
            </div>
            
            <div style='background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 20px; margin-top: 25px;'>
                <h4 style='color: #1976d2; text-align: center; margin-bottom: 15px;'>💡 Success Strategy Framework</h4>
                
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
                    <div style='text-align: center;'>
                        <div style='background: #1976d2; color: white; width: 50px; height: 50px; border-radius: 50%; 
                                   display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 1.5em;'>📚</div>
                        <h5 style='margin: 0 0 5px 0; color: #1976d2;'>Consistent Study</h5>
                        <p style='margin: 0; color: #666; font-size: 0.9em;'>10-15 hours/week</p>
                    </div>
                    
                    <div style='text-align: center;'>
                        <div style='background: #1976d2; color: white; width: 50px; height: 50px; border-radius: 50%; 
                                   display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 1.5em;'>🛠️</div>
                        <h5 style='margin: 0 0 5px 0; color: #1976d2;'>Hands-on Practice</h5>
                        <p style='margin: 0; color: #666; font-size: 0.9em;'>Design & simulate</p>
                    </div>
                    
                    <div style='text-align: center;'>
                        <div style='background: #1976d2; color: white; width: 50px; height: 50px; border-radius: 50%; 
                                   display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 1.5em;'>🔄</div>
                        <h5 style='margin: 0 0 5px 0; color: #1976d2;'>Regular Review</h5>
                        <p style='margin: 0; color: #666; font-size: 0.9em;'>Reinforce learning</p>
                    </div>
                    
                    <div style='text-align: center;'>
                        <div style='background: #1976d2; color: white; width: 50px; height: 50px; border-radius: 50%; 
                                   display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 1.5em;'>👥</div>
                        <h5 style='margin: 0 0 5px 0; color: #1976d2;'>Community</h5>
                        <p style='margin: 0; color: #666; font-size: 0.9em;'>Join forums & groups</p>
                    </div>
                    
                    <div style='text-align: center;'>
                        <div style='background: #1976d2; color: white; width: 50px; height: 50px; border-radius: 50%; 
                                   display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 1.5em;'>📊</div>
                        <h5 style='margin: 0 0 5px 0; color: #1976d2;'>Track Progress</h5>
                        <p style='margin: 0; color: #666; font-size: 0.9em;'>Monitor & adjust</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return widgets.VBox([
            widgets.HTML(overview_html),
            widgets.HTML(roadmap_content),
            widgets.HTML(strategy_html)
        ])
    
    def create_export_system(self) -> widgets.Widget:
        """
        Create comprehensive export functionality with multiple formats and options.
        
        Returns:
            widgets.Widget: Complete export system interface
        """
        export_options = widgets.SelectMultiple(
            options=[
                'Progress Report', 
                'Milestone Timeline', 
                'Detailed Roadmap', 
                'Learning Notes',
                'Analytics Summary',
                'Study Plan'
            ],
            value=['Progress Report'],
            description='Select items:',
            layout=widgets.Layout(width='350px', height='120px'),
            style={'description_width': '100px'}
        )
        
        export_format = widgets.Dropdown(
            options=['CSV', 'JSON', 'HTML Report'],
            value='CSV',
            description='Format:',
            layout=widgets.Layout(width='200px'),
            style={'description_width': '60px'}
        )
        
        export_btn = widgets.Button(
            description='📥 Generate Export',
            button_style='success',
            layout=widgets.Layout(width='160px'),
            tooltip='Export selected data to files'
        )
        
        export_output = widgets.Output()
        
        def generate_export(b):
            """Generate comprehensive exports with multiple format support."""
            with export_output:
                clear_output(wait=True)
                
                try:
                    # Update button state
                    export_btn.description = '📥 Exporting...'
                    export_btn.disabled = True
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    export_count = 0
                    
                    for export_type in export_options.value:
                        try:
                            if export_format.value == 'HTML Report':
                                filename = f"rf_learning_{export_type.lower().replace(' ', '_')}_{timestamp}.html"
                                success = self._export_html_report(export_type, filename)
                            elif export_format.value == 'JSON':
                                filename = f"rf_learning_{export_type.lower().replace(' ', '_')}_{timestamp}.json"
                                success = self._export_json_format(export_type, filename)
                            else:  # CSV
                                filename = f"rf_learning_{export_type.lower().replace(' ', '_')}_{timestamp}.csv"
                                success = self._export_csv_format(export_type, filename)
                            
                            if success:
                                print(f"✅ Exported: {filename}")
                                export_count += 1
                            else:
                                print(f"⚠️ Warning: {export_type} - No data to export")
                                
                        except Exception as e:
                            print(f"❌ Error exporting {export_type}: {e}")
                            logger.error(f"Export error for {export_type}: {e}")
                    
                    if export_count > 0:
                        print(f"\n🎉 Successfully exported {export_count} file(s)!")
                        print("📁 Files saved to current directory")
                    else:
                        print("⚠️ No files were exported. Please check your data and try again.")
                        
                except Exception as e:
                    print(f"❌ Export system error: {e}")
                    logger.error(f"Export system error: {e}")
                finally:
                    # Restore button state
                    export_btn.description = '📥 Generate Export'
                    export_btn.disabled = False
        
        export_btn.on_click(generate_export)
        
        return widgets.VBox([
            widgets.HTML("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #17a2b8, #138496); color: white; border-radius: 10px; margin-bottom: 15px;'>
                <h2 style='margin: 0;'>📥 Export System</h2>
                <p style='margin: 5px 0 0 0; opacity: 0.9;'>Export your learning data for backup and analysis</p>
            </div>
            """),
            
            widgets.VBox([
                widgets.HTML("<h3 style='color: #17a2b8; margin-bottom: 15px;'>📋 Export Configuration</h3>"),
                
                widgets.HBox([
                    widgets.VBox([
                        widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>Select Data to Export:</h4>"),
                        export_options,
                    ], layout=widgets.Layout(margin='0 20px 0 0')),
                    
                    widgets.VBox([
                        widgets.HTML("<h4 style='margin: 0 0 8px 0; color: #555;'>Export Format:</h4>"),
                        export_format,
                        widgets.HTML("<div style='height: 20px;'></div>"),
                        export_btn
                    ])
                ]),
                
                widgets.HTML("<div style='height: 20px;'></div>"),
                
                widgets.HTML("""
                <div style='background: #e8f4f8; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                    <h4 style='color: #17a2b8; margin: 0 0 10px 0;'>💡 Export Options Guide:</h4>
                    <ul style='margin: 0; color: #555; line-height: 1.5;'>
                        <li><strong>Progress Report:</strong> Complete progress tracking data with status and notes</li>
                        <li><strong>Milestone Timeline:</strong> All milestone dates and status information</li>
                        <li><strong>Detailed Roadmap:</strong> Full roadmap structure with priorities and durations</li>
                        <li><strong>Learning Notes:</strong> All your personal learning notes and insights</li>
                        <li><strong>Analytics Summary:</strong> Statistical summary of your learning progress</li>
                        <li><strong>Study Plan:</strong> Personalized study recommendations and next steps</li>
                    </ul>
                </div>
                """),
                
                export_output
            ], layout=widgets.Layout(
                border='2px solid #17a2b8', 
                border_radius='12px',
                padding='20px', 
                margin='10px', 
                background_color='#e8f4f8'
            ))
        ])
    
    def _export_csv_format(self, export_type: str, filename: str) -> bool:
        """
        Export data in CSV format.
        
        Args:
            export_type (str): Type of export
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if export_type == 'Progress Report':
                return self._export_progress_report_csv(filename)
            elif export_type == 'Milestone Timeline':
                return self._export_milestone_timeline_csv(filename)
            elif export_type == 'Detailed Roadmap':
                return self._export_detailed_roadmap_csv(filename)
            elif export_type == 'Learning Notes':
                return self._export_learning_notes_csv(filename)
            elif export_type == 'Analytics Summary':
                return self._export_analytics_summary_csv(filename)
            elif export_type == 'Study Plan':
                return self._export_study_plan_csv(filename)
            return False
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return False
    
    def _export_json_format(self, export_type: str, filename: str) -> bool:
        """
        Export data in JSON format.
        
        Args:
            export_type (str): Type of export
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = {}
            
            if export_type == 'Progress Report':
                data = self._get_progress_data_dict()
            elif export_type == 'Milestone Timeline':
                data = {'milestones': self.milestones}
            elif export_type == 'Detailed Roadmap':
                data = {'roadmap': self.roadmap}
            elif export_type == 'Learning Notes':
                data = self._get_notes_data_dict()
            elif export_type == 'Analytics Summary':
                data = self._get_analytics_data_dict()
            elif export_type == 'Study Plan':
                data = self._get_study_plan_dict()
            
            if data:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                return True
            return False
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return False
    
    def _export_html_report(self, export_type: str, filename: str) -> bool:
        """
        Export data as HTML report.
        
        Args:
            export_type (str): Type of export
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            html_content = self._generate_html_report(export_type)
            if html_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                return True
            return False
        except Exception as e:
            logger.error(f"HTML export error: {e}")
            return False
    
    def _export_progress_report_csv(self, filename: str) -> bool:
        """Export detailed progress report to CSV."""
        try:
            rows = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    for subtopic in topic_data['subtopics']:
                        progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                        rows.append({
                            'Phase': phase_name,
                            'Topic': topic_name,
                            'Subtopic': subtopic,
                            'Priority': topic_data['priority'],
                            'Estimated_Weeks': topic_data['weeks'],
                            'Status': progress_info['status'],
                            'Completion_Percent': progress_info['completion'],
                            'Notes': progress_info['notes'],
                            'Last_Updated': progress_info['last_updated']
                        })
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filename, index=False, encoding='utf-8')
                return True
            return False
        except Exception as e:
            logger.error(f"Progress report CSV export error: {e}")
            return False
    
    def _export_milestone_timeline_csv(self, filename: str) -> bool:
        """Export milestone timeline to CSV."""
        try:
            if not self.milestones:
                return False
            
            rows = []
            for phase, info in self.milestones.items():
                rows.append({
                    'Phase': phase,
                    'Start_Date': info['start_date'],
                    'Target_End_Date': info['target_end_date'],
                    'Actual_End_Date': info.get('actual_end_date', ''),
                    'Status': info['status'],
                    'Duration_Days': (pd.to_datetime(info['target_end_date']) - 
                                    pd.to_datetime(info['start_date'])).days
                })
            
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Milestone timeline CSV export error: {e}")
            return False
    
    def _export_detailed_roadmap_csv(self, filename: str) -> bool:
        """Export complete roadmap structure to CSV."""
        try:
            rows = []
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    for i, subtopic in enumerate(topic_data['subtopics']):
                        rows.append({
                            'Phase': phase_name,
                            'Phase_Type': phase_data['phase'],
                            'Phase_Duration_Weeks': phase_data['duration_weeks'],
                            'Phase_Description': phase_data['description'],
                            'Topic': topic_name,
                            'Topic_Weeks': topic_data['weeks'],
                            'Topic_Priority': topic_data['priority'],
                            'Subtopic_Order': i + 1,
                            'Subtopic': subtopic
                        })
            
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Detailed roadmap CSV export error: {e}")
            return False
    
    def _export_learning_notes_csv(self, filename: str) -> bool:
        """Export all learning notes to CSV."""
        try:
            rows = []
            for key, progress_info in self.progress.items():
                if progress_info['notes'].strip():
                    phase, topic, subtopic = key.split('|', 2)
                    rows.append({
                        'Phase': phase,
                        'Topic': topic,
                        'Subtopic': subtopic,
                        'Status': progress_info['status'],
                        'Completion_Percent': progress_info['completion'],
                        'Notes': progress_info['notes'],
                        'Last_Updated': progress_info['last_updated']
                    })
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filename, index=False, encoding='utf-8')
                return True
            return False
        except Exception as e:
            logger.error(f"Learning notes CSV export error: {e}")
            return False
    
    def _export_analytics_summary_csv(self, filename: str) -> bool:
        """Export analytics summary to CSV."""
        try:
            # Calculate phase statistics
            phase_stats = []
            for phase_name, phase_data in self.roadmap.items():
                total_items = sum(len(topic_data['subtopics']) for topic_data in phase_data['topics'].values())
                completed_items = 0
                in_progress_items = 0
                
                for topic_data in phase_data['topics'].values():
                    for subtopic in topic_data['subtopics']:
                        progress_info = self.get_progress_info(phase_name, "", subtopic)
                        if progress_info['status'] == 'Completed':
                            completed_items += 1
                        elif progress_info['status'] in ['In Progress', 'Review']:
                            in_progress_items += 1
                
                phase_stats.append({
                    'Phase': phase_name,
                    'Total_Items': total_items,
                    'Completed_Items': completed_items,
                    'In_Progress_Items': in_progress_items,
                    'Completion_Rate': (completed_items / total_items * 100) if total_items > 0 else 0,
                    'Phase_Type': phase_data['phase'],
                    'Duration_Weeks': phase_data['duration_weeks']
                })
            
            df = pd.DataFrame(phase_stats)
            df.to_csv(filename, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Analytics summary CSV export error: {e}")
            return False
    
    def _export_study_plan_csv(self, filename: str) -> bool:
        """Export personalized study plan to CSV."""
        try:
            recommendations = self._get_learning_recommendations()
            
            rows = []
            for i, recommendation in enumerate(recommendations, 1):
                rows.append({
                    'Priority': i,
                    'Recommendation': recommendation,
                    'Category': self._categorize_recommendation(recommendation),
                    'Generated_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # Add upcoming items based on progress
            upcoming_items = self._get_upcoming_items()
            for item in upcoming_items:
                rows.append({
                    'Priority': len(rows) + 1,
                    'Recommendation': f"Upcoming: {item['subtopic']} ({item['topic']})",
                    'Category': 'Upcoming',
                    'Generated_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filename, index=False, encoding='utf-8')
                return True
            return False
        except Exception as e:
            logger.error(f"Study plan CSV export error: {e}")
            return False
    
    def _get_upcoming_items(self) -> List[Dict[str, Any]]:
        """Get upcoming learning items based on current progress."""
        upcoming = []
        try:
            for phase_name, phase_data in self.roadmap.items():
                for topic_name, topic_data in phase_data['topics'].items():
                    for subtopic in topic_data['subtopics']:
                        progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                        if (progress_info['status'] == 'Not Started' and 
                            topic_data['priority'] in ['Critical', 'High']):
                            upcoming.append({
                                'subtopic': subtopic,
                                'topic': topic_name,
                                'phase': phase_name.split(':')[0],
                                'priority': topic_data['priority']
                            })
            
            # Sort by priority and limit to top 10
            priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
            upcoming.sort(key=lambda x: priority_order.get(x['priority'], 4))
            return upcoming[:10]
        except:
            return []
    
    def _categorize_recommendation(self, recommendation: str) -> str:
        """Categorize a recommendation for better organization."""
        if 'critical' in recommendation.lower() or 'priority' in recommendation.lower():
            return 'High Priority'
        elif 'review' in recommendation.lower():
            return 'Review'
        elif 'advance' in recommendation.lower() or 'start' in recommendation.lower():
            return 'Progression'
        elif 'focus' in recommendation.lower():
            return 'Focus Area'
        elif 'milestone' in recommendation.lower():
            return 'Milestone'
        else:
            return 'General'
    
    def _get_progress_data_dict(self) -> Dict[str, Any]:
        """Get progress data as dictionary for JSON export."""
        return {
            'progress_data': self.progress,
            'export_timestamp': datetime.now().isoformat(),
            'total_items': len(self.progress),
            'summary': {
                'completed': len([p for p in self.progress.values() if p['status'] == 'Completed']),
                'in_progress': len([p for p in self.progress.values() if p['status'] == 'In Progress']),
                'review': len([p for p in self.progress.values() if p['status'] == 'Review']),
                'not_started': len([p for p in self.progress.values() if p['status'] == 'Not Started'])
            }
        }
    
    def _get_notes_data_dict(self) -> Dict[str, Any]:
        """Get notes data as dictionary for JSON export."""
        notes_data = {}
        for key, progress_info in self.progress.items():
            if progress_info['notes'].strip():
                phase, topic, subtopic = key.split('|', 2)
                notes_data[key] = {
                    'phase': phase,
                    'topic': topic,
                    'subtopic': subtopic,
                    'notes': progress_info['notes'],
                    'status': progress_info['status'],
                    'last_updated': progress_info['last_updated']
                }
        
        return {
            'learning_notes': notes_data,
            'export_timestamp': datetime.now().isoformat(),
            'total_notes': len(notes_data)
        }
    
    def _get_analytics_data_dict(self) -> Dict[str, Any]:
        """Get analytics data as dictionary for JSON export."""
        # This would contain the same analytics data generated in the dashboard
        analytics_data = {
            'export_timestamp': datetime.now().isoformat(),
            'overall_statistics': {},
            'phase_statistics': {},
            'priority_statistics': {},
            'recommendations': self._get_learning_recommendations()
        }
        
        # Calculate statistics (similar to analytics dashboard)
        total_items = len(self.progress) if self.progress else sum(
            len(topic_data['subtopics']) 
            for phase_data in self.roadmap.values() 
            for topic_data in phase_data['topics'].values()
        )
        
        if self.progress:
            completed_items = len([p for p in self.progress.values() if p['status'] == 'Completed'])
            in_progress_items = len([p for p in self.progress.values() if p['status'] == 'In Progress'])
            
            analytics_data['overall_statistics'] = {
                'total_items': total_items,
                'completed_items': completed_items,
                'in_progress_items': in_progress_items,
                'completion_rate': (completed_items / total_items * 100) if total_items > 0 else 0
            }
        
        return analytics_data
    
    def _get_study_plan_dict(self) -> Dict[str, Any]:
        """Get study plan as dictionary for JSON export."""
        return {
            'study_plan': {
                'recommendations': self._get_learning_recommendations(),
                'upcoming_items': self._get_upcoming_items(),
                'generated_date': datetime.now().isoformat()
            },
            'current_focus_areas': self._get_current_focus_areas(),
            'next_milestones': self._get_next_milestones()
        }
    
    def _get_current_focus_areas(self) -> List[str]:
        """Get current focus areas based on in-progress items."""
        focus_areas = []
        try:
            for key, progress_info in self.progress.items():
                if progress_info['status'] in ['In Progress', 'Review']:
                    phase, topic, subtopic = key.split('|', 2)
                    focus_areas.append(f"{topic}: {subtopic}")
        except:
            pass
        return focus_areas[:5]  # Limit to top 5
    
    def _get_next_milestones(self) -> List[Dict[str, str]]:
        """Get upcoming milestones."""
        next_milestones = []
        try:
            current_date = datetime.now().date()
            for phase, info in self.milestones.items():
                if info['status'] in ['Planned', 'Active']:
                    try:
                        target_date = datetime.strptime(info['target_end_date'], '%Y-%m-%d').date()
                        if target_date >= current_date:
                            next_milestones.append({
                                'phase': phase.split(':')[0],
                                'target_date': info['target_end_date'],
                                'status': info['status']
                            })
                    except:
                        continue
            
            # Sort by target date
            next_milestones.sort(key=lambda x: x['target_date'])
        except:
            pass
        
        return next_milestones[:3]  # Limit to next 3
    
    def _generate_html_report(self, export_type: str) -> str:
        """Generate HTML report for specified export type."""
        try:
            html_template = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>RF IC Design Learning Report - {export_type}</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f8f9fa; }}
                    .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px; }}
                    .content {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                    h1 {{ margin: 0; font-size: 2.5em; }}
                    h2 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
                    h3 {{ color: #666; }}
                    .status-completed {{ background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
                    .status-progress {{ background: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
                    .status-review {{ background: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
                    .priority-critical {{ border-left: 5px solid #dc3545; padding-left: 15px; margin: 10px 0; }}
                    .priority-high {{ border-left: 5px solid #fd7e14; padding-left: 15px; margin: 10px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-style: italic; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f8f9fa; font-weight: bold; }}
                    .notes {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; font-style: italic; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>RF IC Design Learning Report</h1>
                    <p>{export_type} - Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                </div>
                <div class="content">
                    {self._get_html_content_for_type(export_type)}
                </div>
                <div class="footer">
                    <p>Generated by RF IC Design Learning Roadmap System</p>
                    <p>Continue your journey to RF IC design mastery! 🚀</p>
                </div>
            </body>
            </html>
            """
            return html_template
        except Exception as e:
            logger.error(f"HTML report generation error: {e}")
            return ""
    
    def _get_html_content_for_type(self, export_type: str) -> str:
        """Generate HTML content for specific export type."""
        try:
            if export_type == 'Progress Report':
                return self._generate_progress_html()
            elif export_type == 'Milestone Timeline':
                return self._generate_milestone_html()
            elif export_type == 'Detailed Roadmap':
                return self._generate_roadmap_html()
            elif export_type == 'Learning Notes':
                return self._generate_notes_html()
            elif export_type == 'Analytics Summary':
                return self._generate_analytics_html()
            elif export_type == 'Study Plan':
                return self._generate_study_plan_html()
            return "<p>Content not available</p>"
        except Exception as e:
            logger.error(f"HTML content generation error: {e}")
            return f"<p>Error generating content: {e}</p>"
    
    def _generate_progress_html(self) -> str:
        """Generate HTML content for progress report."""
        html = "<h2>📈 Learning Progress Report</h2>"
        
        if not self.progress:
            return html + "<p><em>No progress data available yet. Start tracking your learning journey!</em></p>"
        
        # Summary statistics
        total_items = len(self.progress)
        completed = len([p for p in self.progress.values() if p['status'] == 'Completed'])
        in_progress = len([p for p in self.progress.values() if p['status'] == 'In Progress'])
        review = len([p for p in self.progress.values() if p['status'] == 'Review'])
        
        html += f"""
        <div style='background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h3>📊 Overview Statistics</h3>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap;'>
                <div style='text-align: center; margin: 10px;'><strong>{total_items}</strong><br>Total Items</div>
                <div style='text-align: center; margin: 10px;'><strong>{completed}</strong><br>Completed</div>
                <div style='text-align: center; margin: 10px;'><strong>{in_progress}</strong><br>In Progress</div>
                <div style='text-align: center; margin: 10px;'><strong>{review}</strong><br>In Review</div>
                <div style='text-align: center; margin: 10px;'><strong>{(completed/total_items*100):.1f}%</strong><br>Overall Progress</div>
            </div>
        </div>
        """
        
        # Detailed progress table
        html += "<h3>📋 Detailed Progress</h3><table><thead><tr><th>Phase</th><th>Topic</th><th>Subtopic</th><th>Status</th><th>Progress</th><th>Last Updated</th></tr></thead><tbody>"
        
        for key, progress_info in self.progress.items():
            if '|' in key:
                phase, topic, subtopic = key.split('|', 2)
                status_class = f"status-{progress_info['status'].lower().replace(' ', '-')}"
                html += f"""
                <tr>
                    <td>{phase.split(':')[0]}</td>
                    <td>{topic}</td>
                    <td>{subtopic}</td>
                    <td><span class="{status_class}">{progress_info['status']}</span></td>
                    <td>{progress_info['completion']}%</td>
                    <td>{progress_info['last_updated']}</td>
                </tr>
                """
        
        html += "</tbody></table>"
        return html
    
    def _generate_milestone_html(self) -> str:
        """Generate HTML content for milestone timeline."""
        html = "<h2>🎯 Milestone Timeline</h2>"
        
        if not self.milestones:
            return html + "<p><em>No milestones set yet. Create milestones to track your learning timeline!</em></p>"
        
        html += "<div style='margin: 20px 0;'>"
        for phase, info in self.milestones.items():
            status_colors = {'Planned': '#ffc107', 'Active': '#17a2b8', 'Completed': '#28a745', 'Delayed': '#dc3545'}
            color = status_colors.get(info['status'], '#6c757d')
            
            html += f"""
            <div style='border-left: 5px solid {color}; padding: 15px; margin: 15px 0; background: rgba(255,255,255,0.8); border-radius: 0 10px 10px 0;'>
                <h4 style='margin: 0 0 10px 0; color: {color};'>{phase.split(':')[0]}</h4>
                <p><strong>Status:</strong> <span style='background: {color}; color: white; padding: 2px 8px; border-radius: 12px;'>{info['status']}</span></p>
                <p><strong>Start Date:</strong> {info['start_date']}</p>
                <p><strong>Target End Date:</strong> {info['target_end_date']}</p>
                {f"<p><strong>Actual End Date:</strong> {info['actual_end_date']}</p>" if info.get('actual_end_date') else ""}
            </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_roadmap_html(self) -> str:
        """Generate HTML content for detailed roadmap."""
        html = "<h2>🗺️ Detailed Learning Roadmap</h2>"
        
        for i, (phase_name, phase_data) in enumerate(self.roadmap.items(), 1):
            color = self.phase_colors.get(phase_data['phase'], '#6c757d')
            
            html += f"""
            <div style='border: 2px solid {color}; border-radius: 10px; padding: 20px; margin: 20px 0; background: rgba(255,255,255,0.95);'>
                <h3 style='color: {color}; margin-bottom: 10px;'>Phase {i}: {phase_name}</h3>
                <p style='font-style: italic; color: #666;'>{phase_data['description']}</p>
                <p><strong>Duration:</strong> {phase_data['duration_weeks']} weeks | <strong>Type:</strong> {phase_data['phase']}</p>
                
                <h4>Topics:</h4>
            """
            
            for topic_name, topic_data in phase_data['topics'].items():
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(topic_data['priority'], '#6c757d')
                
                html += f"""
                <div class='priority-{topic_data['priority'].lower()}'>
                    <h5>{topic_name} <span style='background: {priority_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;'>{topic_data['priority']}</span></h5>
                    <p><strong>Duration:</strong> {topic_data['weeks']} weeks</p>
                    <ul>
                """
                
                for subtopic in topic_data['subtopics']:
                    html += f"<li>{subtopic}</li>"
                
                html += "</ul></div>"
            
            html += "</div>"
        
        return html
    
    def _generate_notes_html(self) -> str:
        """Generate HTML content for learning notes."""
        html = "<h2>📝 Learning Notes</h2>"
        
        notes_found = False
        for key, progress_info in self.progress.items():
            if progress_info['notes'].strip():
                if not notes_found:
                    notes_found = True
                    html += "<div style='margin: 20px 0;'>"
                
                phase, topic, subtopic = key.split('|', 2)
                html += f"""
                <div style='margin: 20px 0; padding: 15px; border-radius: 10px; background: #f8f9fa; border-left: 4px solid #2196F3;'>
                    <h4 style='margin: 0 0 10px 0; color: #2196F3;'>{subtopic}</h4>
                    <p style='margin: 0 0 5px 0; color: #666; font-size: 0.9em;'><strong>Topic:</strong> {topic} | <strong>Phase:</strong> {phase.split(':')[0]}</p>
                    <div class='notes'>{progress_info['notes'].replace(chr(10), '<br>')}</div>
                    <p style='margin: 5px 0 0 0; color: #999; font-size: 0.8em;'>Last updated: {progress_info['last_updated']}</p>
                </div>
                """
        
        if not notes_found:
            html += "<p><em>No learning notes found. Start adding notes to track your insights and key learnings!</em></p>"
        else:
            html += "</div>"
        
        return html
    
    def _generate_analytics_html(self) -> str:
        """Generate HTML content for analytics summary."""
        html = "<h2>📊 Analytics Summary</h2>"
        
        # Calculate statistics
        phase_stats = {}
        total_items = 0
        completed_items = 0
        
        for phase_name, phase_data in self.roadmap.items():
            phase_total = sum(len(topic_data['subtopics']) for topic_data in phase_data['topics'].values())
            phase_completed = 0
            
            for topic_data in phase_data['topics'].values():
                for subtopic in topic_data['subtopics']:
                    total_items += 1
                    progress_info = self.get_progress_info(phase_name, "", subtopic)
                    if progress_info['status'] == 'Completed':
                        completed_items += 1
                        phase_completed += 1
            
            completion_rate = (phase_completed / phase_total * 100) if phase_total > 0 else 0
            phase_stats[phase_name] = {
                'total': phase_total,
                'completed': phase_completed,
                'completion_rate': completion_rate
            }
        
        # Overall statistics
        overall_completion = (completed_items / total_items * 100) if total_items > 0 else 0
        
        html += f"""
        <div style='background: linear-gradient(135deg, #e8f5e8, #c8e6c9); padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h3>🎯 Overall Performance</h3>
            <div style='font-size: 1.2em; text-align: center;'>
                <strong>{completed_items}/{total_items} items completed ({overall_completion:.1f}%)</strong>
            </div>
        </div>
        
        <h3>📈 Progress by Phase</h3>
        <table>
            <thead>
                <tr><th>Phase</th><th>Completed</th><th>Total</th><th>Completion Rate</th></tr>
            </thead>
            <tbody>
        """
        
        for phase, stats in phase_stats.items():
            html += f"""
            <tr>
                <td>{phase.split(':')[0]}</td>
                <td>{stats['completed']}</td>
                <td>{stats['total']}</td>
                <td>{stats['completion_rate']:.1f}%</td>
            </tr>
            """
        
        html += "</tbody></table>"
        
        # Add recommendations
        recommendations = self._get_learning_recommendations()
        html += "<h3>💡 Current Recommendations</h3><ul>"
        for rec in recommendations[:5]:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        
        return html
    
    def _generate_study_plan_html(self) -> str:
        """Generate HTML content for study plan."""
        html = "<h2>📚 Personalized Study Plan</h2>"
        
        # Current recommendations
        recommendations = self._get_learning_recommendations()
        html += "<h3>🎯 Priority Recommendations</h3><ol>"
        for rec in recommendations:
            html += f"<li style='margin: 8px 0; line-height: 1.5;'>{rec}</li>"
        html += "</ol>"
        
        # Current focus areas
        focus_areas = self._get_current_focus_areas()
        if focus_areas:
            html += "<h3>🔍 Current Focus Areas</h3><ul>"
            for area in focus_areas:
                html += f"<li>{area}</li>"
            html += "</ul>"
        
        # Upcoming milestones
        next_milestones = self._get_next_milestones()
        if next_milestones:
            html += "<h3>📅 Upcoming Milestones</h3><div>"
            for milestone in next_milestones:
                html += f"""
                <div style='padding: 10px; margin: 10px 0; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;'>
                    <strong>{milestone['phase']}</strong> - Target: {milestone['target_date']} ({milestone['status']})
                </div>
                """
            html += "</div>"
        
        # Study tips
        html += f"""
        <h3>💡 Study Success Tips</h3>
        <div style='background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;'>
            <ul style='margin: 0;'>
                <li><strong>Consistency:</strong> Dedicate 10-15 hours per week to study</li>
                <li><strong>Practice:</strong> Implement designs in simulation tools</li>
                <li><strong>Review:</strong> Regularly revisit completed topics</li>
                <li><strong>Application:</strong> Connect theory to real-world examples</li>
                <li><strong>Community:</strong> Join RF/IC design forums and discussions</li>
            </ul>
        </div>
        """
        
        return html
    
    def display_full_system(self) -> widgets.Widget:
        """
        Display the complete learning roadmap system with all features.
        
        Returns:
            widgets.Widget: Complete system interface
        """
        try:
            # Create tabs for different sections
            tab_contents = [
                self.create_roadmap_overview(),
                self.create_progress_manager(),
                self.create_milestone_manager(),
                self.create_analytics_dashboard(),
                self.create_export_system()
            ]
            
            tab_titles = [
                '🗺️ Roadmap Overview',
                '📈 Progress Tracker',
                '🎯 Milestones',
                '📊 Analytics',
                '📥 Export'
            ]
            
            tabs = widgets.Tab()
            tabs.children = tab_contents
            for i, title in enumerate(tab_titles):
                tabs.set_title(i, title)
            
            # Enhanced header with system information
            header = widgets.HTML(f"""
            <div style='text-align: center; padding: 25px; background: linear-gradient(45deg, #667eea, #764ba2); 
                        color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
                <h1 style='margin: 0 0 10px 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                    🎯 RF IC Design Learning Roadmap System
                </h1>
                <p style='margin: 5px 0 15px 0; font-size: 1.3em; opacity: 0.95;'>
                    Your comprehensive journey from fundamentals to mastery
                </p>
                <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin-top: 15px;'>
                    <div style='display: flex; justify-content: space-around; flex-wrap: wrap;'>
                        <div style='margin: 5px;'><strong>🏗️ Foundation</strong><br>0-3 months</div>
                        <div style='margin: 5px;'><strong>🚀 Short-term</strong><br>3-9 months</div>
                        <div style='margin: 5px;'><strong>⚡ Mid-term</strong><br>9-18 months</div>
                        <div style='margin: 5px;'><strong>🏆 Long-term</strong><br>18-30 months</div>
                        <div style='margin: 5px;'><strong>🌟 Advanced</strong><br>30+ months</div>
                    </div>
                </div>
            </div>
            """)
            
            # System information and quick stats
            system_info = widgets.HTML(f"""
            <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 20px; border-radius: 12px; 
                        margin-bottom: 20px; border: 2px solid #dee2e6;'>
                <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>📊 System Status</h4>
                        <p style='margin: 0; color: #6c757d;'>Ready for learning tracking</p>
                    </div>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>💾 Data Files</h4>
                        <p style='margin: 0; color: #6c757d;'>
                            Progress: {"✅" if os.path.exists(self.progress_file) else "📝"} | 
                            Milestones: {"✅" if os.path.exists(self.milestones_file) else "📝"}
                        </p>
                    </div>
                    <div style='margin: 10px;'>
                        <h4 style='margin: 0 0 5px 0; color: #495057;'>🎯 Quick Stats</h4>
                        <p style='margin: 0; color: #6c757d;'>
                            {len(self.progress)} items tracked | 
                            {len(self.milestones)} milestones set
                        </p>
                    </div>
                </div>
            </div>
            """)
            
            return widgets.VBox([
                header,
                system_info,
                tabs
            ])
            
        except Exception as e:
            logger.error(f"Error displaying full system: {e}")
            return widgets.HTML(f"<p>Error loading system: {e}</p>")

# Performance optimized system creation function
def create_rf_learning_system() -> widgets.Widget:
    """
    Create and initialize the RF learning roadmap system with optimizations.
    
    Returns:
        widgets.Widget: Complete learning system interface
    """
    try:
        # Initialize system with progress indication
        print("🚀 Initializing RF IC Design Learning Roadmap System...")
        print("📊 Loading comprehensive 5-phase learning framework...")
        
        # Create system instance
        system = RFLearningRoadmapSystem()
        
        print("✅ System Initialization Complete!")
        print("\n" + "="*60)
        print("🎯 RF IC DESIGN LEARNING ROADMAP SYSTEM")
        print("="*60)

        """
        print("📋 System Features:")
        print("  • 🗺️  Comprehensive 5-phase learning roadmap (144+ weeks)")
        print("  • 📈 Advanced progress tracking for 100+ subtopics")
        print("  • 🎯 Smart milestone management with timeline visualization")
        print("  • 📊 Analytics dashboard with intelligent insights")
        print("  • 📥 Multi-format export system (CSV, JSON, HTML)")
        print("  • 🎨 Modern, responsive user interface")
        print("  • 💾 Persistent data storage with auto-backup")
        print()
        print("🎓 Learning Path Focus:")
        print("  📐 Mathematics & Circuit Theory → 📱 Analog IC Design")
        print("  ⚡ Advanced Microwave & SerDes → 📡 RF IC Mastery")
        print("  🌟 Cutting-edge Applications (5G, mmWave, Automotive)")
        print()
        print("💡 Pro Tips:")
        print("  • Start with the 'Roadmap Overview' tab to understand the complete journey")
        print("  • Use 'Progress Tracker' to log your daily learning and notes")
        print("  • Set milestones to stay motivated and track timeline progress")
        print("  • Check 'Analytics' regularly for personalized recommendations")
        print("  • Export your data periodically for backup and analysis")
        print()
        print("🚀 Ready to begin your RF IC Design mastery journey!")
        print("="*60)
        """
        return system.display_full_system()
        
    except Exception as e:
        logger.error(f"Error creating learning system: {e}")
        error_widget = widgets.HTML(f"""
        <div style='padding: 30px; text-align: center; background: #f8d7da; border: 2px solid #f5c6cb; 
                    border-radius: 10px; color: #721c24;'>
            <h2>⚠️ System Initialization Error</h2>
            <p>Error details: {e}</p>
            <p>Please check the logs and try again.</p>
        </div>
        """)
        return error_widget

# Main execution block with error handling
if __name__ == "__main__":
    try:
        learning_system = create_rf_learning_system()
        display(learning_system)
    except Exception as e:
        print(f"❌ Critical Error: Unable to start the learning system")
        print(f"Error details: {e}")
        logger.error(f"Critical startup error: {e}")
        
        # Display basic error information
        error_display = widgets.HTML(f"""
        <div style='padding: 20px; background: #f8d7da; border-radius: 10px; color: #721c24;'>
            <h3>⚠️ System Error</h3>
            <p>The RF IC Design Learning Roadmap System encountered an error during startup.</p>
            <p><strong>Error:</strong> {e}</p>
            <p>Please restart the notebook kernel and try again.</p>
        </div>
        """)
        display(error_display)
