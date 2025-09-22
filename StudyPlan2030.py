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
warnings.filterwarnings('ignore')

class RFLearningRoadmapSystem:
    def __init__(self, csv_file='rf_learning_roadmap.csv'):
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
        
        # Initialize the comprehensive roadmap
        self.roadmap = self.create_comprehensive_roadmap()
        self.load_all_data()
        
    def create_comprehensive_roadmap(self):
        """Create a comprehensive learning roadmap"""
        return {
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
    
    def load_all_data(self):
        """Load all data from CSV files"""
        self.load_progress()
        self.load_milestones()
        
    def load_progress(self):
        """Load learning progress"""
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
            else:
                self.progress = {}
        except Exception as e:
            print(f"❌ Error loading progress: {e}")
            self.progress = {}
    
    def load_milestones(self):
        """Load milestone data"""
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
            else:
                self.milestones = {}
        except Exception as e:
            print(f"❌ Error loading milestones: {e}")
            self.milestones = {}
    
    def save_progress(self):
        """Save progress to CSV"""
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
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
    
    def save_milestones(self):
        """Save milestones to CSV"""
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
        except Exception as e:
            print(f"❌ Error saving milestones: {e}")
    
    def get_progress_info(self, phase, topic, subtopic):
        """Get progress information for a specific item"""
        key = f"{phase}|{topic}|{subtopic}"
        return self.progress.get(key, {
            'status': 'Not Started',
            'completion': 0,
            'notes': '',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def set_progress_info(self, phase, topic, subtopic, status, completion, notes):
        """Set progress information"""
        key = f"{phase}|{topic}|{subtopic}"
        self.progress[key] = {
            'status': status,
            'completion': completion,
            'notes': notes,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_progress()
    
    def create_progress_manager(self):
        """Create progress management interface"""
        # Phase selection
        phase_dropdown = widgets.Dropdown(
            options=['-- Select Phase --'] + list(self.roadmap.keys()),
            value='-- Select Phase --',
            description='Phase:',
            layout=widgets.Layout(width='400px')
        )
        
        # Topic selection
        topic_dropdown = widgets.Dropdown(
            options=['-- Select Topic --'],
            value='-- Select Topic --',
            description='Topic:',
            layout=widgets.Layout(width='400px')
        )
        
        # Subtopic selection
        subtopic_dropdown = widgets.Dropdown(
            options=['-- Select Subtopic --'],
            value='-- Select Subtopic --',
            description='Subtopic:',
            layout=widgets.Layout(width='400px')
        )
        
        # Status and completion
        status_dropdown = widgets.Dropdown(
            options=['Not Started', 'In Progress', 'Review', 'Completed', 'Skipped'],
            value='Not Started',
            description='Status:',
            layout=widgets.Layout(width='200px')
        )
        
        completion_slider = widgets.IntSlider(
            value=0,
            min=0,
            max=100,
            step=5,
            description='Progress:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='300px')
        )
        
        # Notes
        notes_area = widgets.Textarea(
            placeholder='Add your learning notes here...',
            layout=widgets.Layout(width='500px', height='120px'),
            disabled=True
        )
        
        # Save button
        save_btn = widgets.Button(
            description='Save Progress',
            button_style='success',
            layout=widgets.Layout(width='120px')
        )
        
        # Current selection info
        selection_info = widgets.HTML(
            value="<p><i>Select a subtopic to track your progress...</i></p>"
        )
        
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
            
            if (selected_topic == '-- Select Topic --' or 
                selected_phase == '-- Select Phase --'):
                subtopic_dropdown.options = ['-- Select Subtopic --']
                return
            
            subtopics = self.roadmap[selected_phase]['topics'][selected_topic]['subtopics']
            subtopic_dropdown.options = ['-- Select Subtopic --'] + subtopics
            subtopic_dropdown.value = '-- Select Subtopic --'
        
        def update_progress_fields(change=None):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if (selected_subtopic == '-- Select Subtopic --' or
                selected_topic == '-- Select Topic --' or
                selected_phase == '-- Select Phase --'):
                notes_area.disabled = True
                notes_area.value = ''
                selection_info.value = "<p><i>Select a subtopic to track your progress...</i></p>"
                return
            
            # Load existing progress
            progress_info = self.get_progress_info(selected_phase, selected_topic, selected_subtopic)
            status_dropdown.value = progress_info['status']
            completion_slider.value = progress_info['completion']
            notes_area.value = progress_info['notes']
            notes_area.disabled = False
            
            # Update selection info
            topic_weeks = self.roadmap[selected_phase]['topics'][selected_topic]['weeks']
            priority = self.roadmap[selected_phase]['topics'][selected_topic]['priority']
            selection_info.value = f"""
            <div style='background: #f0f0f0; padding: 10px; border-radius: 5px;'>
                <strong>Current Selection:</strong> {selected_phase} → {selected_topic} → {selected_subtopic}<br>
                <strong>Priority:</strong> {priority} | <strong>Estimated Duration:</strong> {topic_weeks} weeks<br>
                <strong>Last Updated:</strong> {progress_info['last_updated']}
            </div>
            """
        
        def save_progress_info(b):
            selected_phase = phase_dropdown.value
            selected_topic = topic_dropdown.value
            selected_subtopic = subtopic_dropdown.value
            
            if (selected_subtopic != '-- Select Subtopic --' and
                selected_topic != '-- Select Topic --' and
                selected_phase != '-- Select Phase --'):
                
                self.set_progress_info(
                    selected_phase, selected_topic, selected_subtopic,
                    status_dropdown.value, completion_slider.value, notes_area.value
                )
                print(f"✅ Progress saved for: {selected_subtopic}")
        
        # Set up observers
        phase_dropdown.observe(update_topic_options, names='value')
        topic_dropdown.observe(update_subtopic_options, names='value')
        subtopic_dropdown.observe(update_progress_fields, names='value')
        save_btn.on_click(save_progress_info)
        
        return widgets.VBox([
            widgets.HTML("<h2>📈 Learning Progress Manager</h2>"),
            
            # Selection area
            widgets.VBox([
                widgets.HTML("<h3>🎯 Select Learning Item:</h3>"),
                phase_dropdown,
                topic_dropdown,
                subtopic_dropdown,
                selection_info
            ], layout=widgets.Layout(border='2px solid #4CAF50', border_radius='10px',
                                   padding='15px', margin='10px', background_color='#f8f9fa')),
            
            # Progress tracking
            widgets.VBox([
                widgets.HTML("<h3>📊 Track Progress:</h3>"),
                widgets.HBox([status_dropdown, completion_slider]),
                notes_area,
                save_btn
            ], layout=widgets.Layout(border='2px solid #2196F3', border_radius='10px',
                                   padding='15px', margin='10px', background_color='#e3f2fd'))
        ])
    
    def create_milestone_manager(self):
        """Create milestone management interface"""
        # Phase selection for milestones
        milestone_phase_dropdown = widgets.Dropdown(
            options=list(self.roadmap.keys()),
            description='Phase:',
            layout=widgets.Layout(width='400px')
        )
        
        # Date pickers
        start_date = widgets.DatePicker(
            description='Start Date:',
            value=datetime.now().date(),
            layout=widgets.Layout(width='200px')
        )
        
        end_date = widgets.DatePicker(
            description='Target End:',
            value=(datetime.now() + timedelta(weeks=12)).date(),
            layout=widgets.Layout(width='200px')
        )
        
        milestone_status = widgets.Dropdown(
            options=['Planned', 'Active', 'Completed', 'Delayed'],
            value='Planned',
            description='Status:',
            layout=widgets.Layout(width='150px')
        )
        
        # Buttons
        set_milestone_btn = widgets.Button(
            description='Set Milestone',
            button_style='primary',
            layout=widgets.Layout(width='120px')
        )
        
        # Milestone display
        milestone_display = widgets.HTML()
        
        def update_milestone_display():
            if not self.milestones:
                milestone_display.value = "<p><i>No milestones set yet.</i></p>"
                return
            
            html_content = "<h4>📅 Current Milestones:</h4><div style='max-height: 300px; overflow-y: auto;'>"
            for phase, info in self.milestones.items():
                status_color = {'Planned': '#ffc107', 'Active': '#17a2b8', 
                              'Completed': '#28a745', 'Delayed': '#dc3545'}.get(info['status'], '#6c757d')
                
                html_content += f"""
                <div style='border: 1px solid {status_color}; border-radius: 8px; padding: 10px; margin: 5px; background: rgba(255,255,255,0.8);'>
                    <strong>{phase}</strong> 
                    <span style='color: {status_color}; font-weight: bold;'>[{info['status']}]</span><br>
                    <small>📅 {info['start_date']} → {info['target_end_date']}</small>
                </div>
                """
            html_content += "</div>"
            milestone_display.value = html_content
        
        def set_milestone(b):
            selected_phase = milestone_phase_dropdown.value
            self.milestones[selected_phase] = {
                'start_date': start_date.value.strftime('%Y-%m-%d'),
                'target_end_date': end_date.value.strftime('%Y-%m-%d'),
                'actual_end_date': '',
                'status': milestone_status.value
            }
            self.save_milestones()
            update_milestone_display()
            print(f"✅ Milestone set for: {selected_phase}")
        
        set_milestone_btn.on_click(set_milestone)
        update_milestone_display()
        
        return widgets.VBox([
            widgets.HTML("<h2>🎯 Milestone Manager</h2>"),
            widgets.VBox([
                widgets.HTML("<h3>📅 Set New Milestone:</h3>"),
                milestone_phase_dropdown,
                widgets.HBox([start_date, end_date, milestone_status]),
                set_milestone_btn
            ], layout=widgets.Layout(border='2px solid #FF9800', border_radius='10px',
                                   padding='15px', margin='10px', background_color='#fff8e1')),
            milestone_display
        ])
    
    def create_analytics_dashboard(self):
        """Create analytics and visualization dashboard"""
        analytics_output = widgets.Output()
        
        refresh_btn = widgets.Button(
            description='Refresh Analytics',
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        
        def generate_analytics(b=None):
            with analytics_output:
                clear_output(wait=True)
                
                # Calculate overall progress
                total_items = 0
                completed_items = 0
                in_progress_items = 0
                
                phase_stats = {}
                for phase_name, phase_data in self.roadmap.items():
                    phase_total = 0
                    phase_completed = 0
                    phase_in_progress = 0
                    
                    for topic_name, topic_data in phase_data['topics'].items():
                        for subtopic in topic_data['subtopics']:
                            total_items += 1
                            phase_total += 1
                            
                            progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                            if progress_info['status'] == 'Completed':
                                completed_items += 1
                                phase_completed += 1
                            elif progress_info['status'] in ['In Progress', 'Review']:
                                in_progress_items += 1
                                phase_in_progress += 1
                    
                    phase_stats[phase_name] = {
                        'total': phase_total,
                        'completed': phase_completed,
                        'in_progress': phase_in_progress,
                        'completion_rate': (phase_completed / phase_total * 100) if phase_total > 0 else 0
                    }
                
                # Create visualizations
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle('RF IC Design Learning Analytics Dashboard', fontsize=16, fontweight='bold')
                
                # Overall progress pie chart
                overall_not_started = total_items - completed_items - in_progress_items
                ax1.pie([completed_items, in_progress_items, overall_not_started],
                       labels=['Completed', 'In Progress', 'Not Started'],
                       colors=['#28a745', '#ffc107', '#dc3545'],
                       autopct='%1.1f%%', startangle=90)
                ax1.set_title('Overall Progress Distribution')
                
                # Progress by phase
                phases = list(phase_stats.keys())
                completion_rates = [phase_stats[phase]['completion_rate'] for phase in phases]
                colors = [self.phase_colors.get(self.roadmap[phase]['phase'], '#6c757d') for phase in phases]
                
                bars = ax2.bar(range(len(phases)), completion_rates, color=colors)
                ax2.set_xlabel('Learning Phases')
                ax2.set_ylabel('Completion Rate (%)')
                ax2.set_title('Progress by Phase')
                ax2.set_xticks(range(len(phases)))
                ax2.set_xticklabels([phase.split(':')[0] for phase in phases], rotation=45, ha='right')
                ax2.set_ylim(0, 100)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.1f}%', ha='center', va='bottom')
                
                # Timeline view (if milestones are set)
                if self.milestones:
                    milestone_phases = []
                    start_dates = []
                    end_dates = []
                    
                    for phase, info in self.milestones.items():
                        if info['start_date'] and info['target_end_date']:
                            milestone_phases.append(phase.split(':')[0])
                            start_dates.append(pd.to_datetime(info['start_date']))
                            end_dates.append(pd.to_datetime(info['target_end_date']))
                    
                    if milestone_phases:
                        y_pos = np.arange(len(milestone_phases))
                        durations = [(end - start).days for start, end in zip(start_dates, end_dates)]
                        
                        bars = ax3.barh(y_pos, durations, left=[d.toordinal() for d in start_dates])
                        ax3.set_yticks(y_pos)
                        ax3.set_yticklabels(milestone_phases)
                        ax3.set_xlabel('Timeline')
                        ax3.set_title('Learning Phase Timeline')
                        
                        # Format x-axis as dates
                        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
                else:
                    ax3.text(0.5, 0.5, 'Set milestones to view timeline', 
                            ha='center', va='center', transform=ax3.transAxes,
                            fontsize=12, style='italic')
                    ax3.set_title('Learning Phase Timeline')
                
                # Priority distribution
                priority_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                for phase_data in self.roadmap.values():
                    for topic_data in phase_data['topics'].values():
                        priority_counts[topic_data['priority']] += len(topic_data['subtopics'])
                
                priorities = list(priority_counts.keys())
                counts = list(priority_counts.values())
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 
                                 'Medium': '#ffc107', 'Low': '#28a745'}
                colors = [priority_colors[p] for p in priorities]
                
                ax4.bar(priorities, counts, color=colors)
                ax4.set_xlabel('Priority Level')
                ax4.set_ylabel('Number of Subtopics')
                ax4.set_title('Learning Items by Priority')
                
                # Add value labels
                for i, count in enumerate(counts):
                    ax4.text(i, count + 0.5, str(count), ha='center', va='bottom')
                
                plt.tight_layout()
                plt.show()
                
                # Display summary statistics
                print("\n" + "="*60)
                print("📊 LEARNING PROGRESS SUMMARY")
                print("="*60)
                print(f"📈 Overall Progress: {completed_items}/{total_items} completed ({completed_items/total_items*100:.1f}%)")
                print(f"🔄 Currently In Progress: {in_progress_items} items")
                print(f"⏳ Not Started: {total_items - completed_items - in_progress_items} items")
                print("\n📋 Progress by Phase:")
                
                for phase, stats in phase_stats.items():
                    phase_short = phase.split(':')[0]
                    print(f"  • {phase_short}: {stats['completed']}/{stats['total']} ({stats['completion_rate']:.1f}%)")
                
                # Show next recommendations
                print(f"\n🎯 RECOMMENDED NEXT STEPS:")
                recommendations = self.get_learning_recommendations()
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {rec}")
        
        refresh_btn.on_click(generate_analytics)
        generate_analytics()  # Initial load
        
        return widgets.VBox([
            widgets.HTML("<h2>📊 Learning Analytics Dashboard</h2>"),
            refresh_btn,
            analytics_output
        ])
    
    def get_learning_recommendations(self):
        """Generate learning recommendations based on current progress"""
        recommendations = []
        
        # Check for critical items not started
        for phase_name, phase_data in self.roadmap.items():
            for topic_name, topic_data in phase_data['topics'].items():
                if topic_data['priority'] == 'Critical':
                    for subtopic in topic_data['subtopics']:
                        progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                        if progress_info['status'] == 'Not Started':
                            recommendations.append(f"Start critical topic: {subtopic} ({topic_name})")
        
        # Check for items in review status
        for phase_name, phase_data in self.roadmap.items():
            for topic_name, topic_data in phase_data['topics'].items():
                for subtopic in topic_data['subtopics']:
                    progress_info = self.get_progress_info(phase_name, topic_name, subtopic)
                    if progress_info['status'] == 'Review':
                        recommendations.append(f"Complete review: {subtopic}")
        
        # Check for sequential dependencies
        phase_order = list(self.roadmap.keys())
        for i, phase_name in enumerate(phase_order[:-1]):
            next_phase = phase_order[i + 1]
            current_completion = self.calculate_phase_completion(phase_name)
            next_phase_started = self.has_phase_started(next_phase)
            
            if current_completion > 70 and not next_phase_started:
                recommendations.append(f"Consider starting: {next_phase.split(':')[0]}")
        
        return recommendations if recommendations else ["Great progress! Continue with your current learning plan."]
    
    def calculate_phase_completion(self, phase_name):
        """Calculate completion percentage for a phase"""
        if phase_name not in self.roadmap:
            return 0
        
        total_items = 0
        completed_items = 0
        
        for topic_data in self.roadmap[phase_name]['topics'].values():
            for subtopic in topic_data['subtopics']:
                total_items += 1
                progress_info = self.get_progress_info(phase_name, "", subtopic)
                if progress_info['status'] == 'Completed':
                    completed_items += 1
        
        return (completed_items / total_items * 100) if total_items > 0 else 0
    
    def has_phase_started(self, phase_name):
        """Check if any item in a phase has been started"""
        if phase_name not in self.roadmap:
            return False
        
        for topic_data in self.roadmap[phase_name]['topics'].values():
            for subtopic in topic_data['subtopics']:
                progress_info = self.get_progress_info(phase_name, "", subtopic)
                if progress_info['status'] != 'Not Started':
                    return True
        return False
    
    def create_roadmap_overview(self):
        """Create a comprehensive roadmap overview"""
        overview_html = """
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <h1 style='text-align: center; margin-bottom: 10px;'>🎯 Learning Roadmap</h1>
            <p style='text-align: center; font-size: 1.1em;'>Comprehensive 30+ month journey from fundamentals to mastery</p>
        </div>
        """
        
        # Create detailed roadmap display
        roadmap_content = ""
        
        for phase_name, phase_data in self.roadmap.items():
            color = self.phase_colors.get(phase_data['phase'], '#6c757d')
            phase_short = phase_name.split(':')[0] if ':' in phase_name else phase_name
            
            roadmap_content += f"""
            <div style='border: 3px solid {color}; border-radius: 12px; padding: 20px; margin: 15px 0; background: rgba(255,255,255,0.95);'>
                <h2 style='color: {color}; margin-bottom: 10px;'>{phase_name}</h2>
                <p style='font-style: italic; margin-bottom: 15px; color: #666;'>{phase_data['description']}</p>
                <p><strong>Duration:</strong> {phase_data['duration_weeks']} weeks | <strong>Phase:</strong> {phase_data['phase']}</p>
                
                <div style='margin-top: 20px;'>
            """
            
            for topic_name, topic_data in phase_data['topics'].items():
                priority_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
                priority_color = priority_colors.get(topic_data['priority'], '#6c757d')
                
                roadmap_content += f"""
                    <div style='border-left: 4px solid {priority_color}; padding-left: 15px; margin: 15px 0;'>
                        <h4 style='color: #333; margin-bottom: 8px;'>{topic_name}</h4>
                        <p><span style='background: {priority_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;'>{topic_data['priority']}</span> 
                        <strong>Duration:</strong> {topic_data['weeks']} weeks</p>
                        <ul style='margin: 10px 0; padding-left: 20px;'>
                """
                
                for subtopic in topic_data['subtopics']:
                    roadmap_content += f"<li style='margin: 3px 0; color: #555;'>{subtopic}</li>"
                
                roadmap_content += "</ul></div>"
            
            roadmap_content += "</div></div>"
        
        # Learning strategy section
        strategy_html = f"""
        <div style='background: #f8f9fa; border: 2px solid #28a745; border-radius: 10px; padding: 20px; margin: 20px 0;'>
            <h2 style='color: #28a745;'>📋 Learning Strategy Overview</h2>
            
            <div style='display: flex; flex-wrap: wrap; justify-content: space-around; margin: 20px 0;'>
                <div style='flex: 1; min-width: 250px; margin: 10px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h3 style='color: {self.phase_colors["Short-term"]}; text-align: center;'>🎯 Short-term (3-9 months)</h3>
                    <ul style='color: #555;'>
                        <li>Master Analog IC design fundamentals</li>
                        <li>Build strong circuit theory foundation</li>
                        <li>Prepare for microwave engineering</li>
                        <li>Focus on practical design skills</li>
                    </ul>
                </div>
                
                <div style='flex: 1; min-width: 250px; margin: 10px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h3 style='color: {self.phase_colors["Mid-term"]}; text-align: center;'>🚀 Mid-term (9-18 months)</h3>
                    <ul style='color: #555;'>
                        <li>Advanced microwave engineering</li>
                        <li>High-speed SerDes design</li>
                        <li>EM simulation mastery</li>
                        <li>System-level thinking</li>
                    </ul>
                </div>
                
                <div style='flex: 1; min-width: 250px; margin: 10px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h3 style='color: {self.phase_colors["Long-term"]}; text-align: center;'>🏆 Long-term (18-30 months)</h3>
                    <ul style='color: #555;'>
                        <li>RF IC design expertise</li>
                        <li>System architecture design</li>
                        <li>Advanced integration techniques</li>
                        <li>Industry-level competency</li>
                    </ul>
                </div>
            </div>
            
            <div style='background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 20px;'>
                <h4 style='color: #1976d2;'>💡 Key Success Factors:</h4>
                <ul style='color: #555;'>
                    <li><strong>Consistent Progress:</strong> Aim for 10-15 hours per week of focused study</li>
                    <li><strong>Practical Application:</strong> Implement designs in simulation tools</li>
                    <li><strong>Knowledge Integration:</strong> Connect theory with real-world applications</li>
                    <li><strong>Regular Review:</strong> Revisit fundamentals while learning advanced topics</li>
                    <li><strong>Community Engagement:</strong> Join RF/IC design forums and conferences</li>
                </ul>
            </div>
        </div>
        """
        
        return widgets.VBox([
            widgets.HTML(overview_html),
            widgets.HTML(roadmap_content),
            widgets.HTML(strategy_html)
        ])
    
    def create_export_system(self):
        """Create comprehensive export functionality"""
        export_options = widgets.SelectMultiple(
            options=['Progress Report', 'Milestone Timeline', 'Detailed Roadmap', 'Learning Notes'],
            value=['Progress Report'],
            description='Export:',
            layout=widgets.Layout(width='300px', height='100px')
        )
        
        export_btn = widgets.Button(
            description='Generate Export',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        
        export_output = widgets.Output()
        
        def generate_export(b):
            with export_output:
                clear_output(wait=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                for export_type in export_options.value:
                    filename = f"rf_learning_{export_type.lower().replace(' ', '_')}_{timestamp}.csv"
                    
                    if export_type == 'Progress Report':
                        self.export_progress_report(filename)
                    elif export_type == 'Milestone Timeline':
                        self.export_milestone_timeline(filename)
                    elif export_type == 'Detailed Roadmap':
                        self.export_detailed_roadmap(filename)
                    elif export_type == 'Learning Notes':
                        self.export_learning_notes(filename)
                    
                    print(f"✅ Exported: {filename}")
        
        export_btn.on_click(generate_export)
        
        return widgets.VBox([
            widgets.HTML("<h2>📥 Export System</h2>"),
            widgets.VBox([
                export_options,
                export_btn,
                export_output
            ], layout=widgets.Layout(border='2px solid #17a2b8', border_radius='10px',
                                   padding='15px', margin='10px', background_color='#e8f4f8'))
        ])
    
    def export_progress_report(self, filename):
        """Export detailed progress report"""
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
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        return df
    
    def export_milestone_timeline(self, filename):
        """Export milestone timeline"""
        if not self.milestones:
            print("⚠️ No milestones set to export")
            return
        
        rows = []
        for phase, info in self.milestones.items():
            rows.append({
                'Phase': phase,
                'Start_Date': info['start_date'],
                'Target_End_Date': info['target_end_date'],
                'Actual_End_Date': info.get('actual_end_date', ''),
                'Status': info['status'],
                'Duration_Days': (pd.to_datetime(info['target_end_date']) - pd.to_datetime(info['start_date'])).days
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        return df
    
    def export_detailed_roadmap(self, filename):
        """Export complete roadmap structure"""
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
        df.to_csv(filename, index=False)
        return df
    
    def export_learning_notes(self, filename):
        """Export all learning notes"""
        rows = []
        for key, progress_info in self.progress.items():
            if progress_info['notes'].strip():
                phase, topic, subtopic = key.split('|', 2)
                rows.append({
                    'Phase': phase,
                    'Topic': topic,
                    'Subtopic': subtopic,
                    'Notes': progress_info['notes'],
                    'Last_Updated': progress_info['last_updated']
                })
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False)
            return df
        else:
            print("⚠️ No notes found to export")
            return None
    
    def display_full_system(self):
        """Display the complete learning roadmap system"""
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
        
        # Header
        header = widgets.HTML("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 15px; margin-bottom: 20px;'>
            <h1 style='margin: 0; font-size: 2.5em;'>🎯 Learning Roadmap</h1>
            <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;'>Your complete journey from fundamentals to RF IC mastery</p>
        </div>
        """)
        
        return widgets.VBox([header, tabs])

# Usage and initialization
def create_rf_learning_system():
    """Create and initialize the RF learning roadmap system"""
    system = RFLearningRoadmapSystem()
    
    print("🚀 RF IC Design Learning Roadmap System Initialized!")
    print("📋 System Features:")
    print("  • Comprehensive 5-phase learning roadmap (30+ months)")
    print("  • Progress tracking for 100+ subtopics")
    print("  • Milestone management with timeline visualization")
    print("  • Analytics dashboard with progress insights")
    print("  • Export functionality for backup and analysis")
    print("  • Strategic focus: Analog IC → Microwave → SerDes → RF IC")
    print()
    
    return system.display_full_system()

# Main execution
if __name__ == "__main__":
    learning_system = create_rf_learning_system()
    display(learning_system)
