#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ipyvuetify as v
import ipywidgets as widgets
import plotly.graph_objects as go
from .utils import add_tooltip, create_eq


# ### Import Sheet

# In[2]:


class CustomCard(v.Card):
    def __init__(self, icon, title, text, value=''):
        super().__init__()
        self.class_ = 'd-flex flex-column ma-4 pa-2 justify-center align-center'
        self.style_ = 'border-radius:20px; width:260px; min-height:400px'
        self.elevation = 0
        self.outlined = True
        self.v_model = None
        
        self.value = value
        
        self.icon = v.Icon(children=[icon],
                           size='48px',
                           class_='ma-3 mt-6')
        self.title = v.CardTitle(children=[title])
        self.text = v.CardText(children=[text])
        
        self.children = [self.icon, self.title, self.text]
        
    def select(self):
        self.dark = True
        self.color = '#007960'
    
    def deselect(self):
        self.dark = False
        self.color = None


# In[3]:


class ImportModel(v.Card):
    def __init__(self):
        class_ = 'd-flex justify-center'
        elevation = 0
        color = 'blue darken-5'
        style_ = 'border-radius:20px; width=700px'
        super().__init__(class_=class_, 
                         style_=style_,
                         # color=color,
                         elevation=elevation)
        self.selected = None
        
        self.worksheet_card = CustomCard(icon='mdi-book', 
                                         title='Worksheet URL',
                                         text='Pull the model from a seeq worksheet url.',
                                         value='worksheet')
        
        self.sysid_card = CustomCard(icon='mdi-puzzle', 
                                     title='SysID Add-on',
                                     text='Import the model from SysID results.',
                                     value='sysid')
        
        self.user_card = CustomCard(icon='mdi-account', 
                                     title='User-Defined',
                                     text='Create a custom model by defining gain, time-constant, order, etc.',
                                     value='user')
        self.user_card.icon.class_ = 'ma-3 mt-10 mb-1'
        
        self.options_list = [self.worksheet_card, self.sysid_card, self.user_card]
        
        options_dict = {}
        for option in self.options_list:
            options_dict[option.value] = option
        self.options_dict = options_dict
        
        for item in self.options_list:
            item.on_event('click', self.select_action)
        
        self.options_container = v.Card(children=self.options_list,
                                        class_ = 'd-flex flex-row ma-4 pa-4 justify-center',
                                        style_='border-radius:20px',
                                        color = 'grey lighten-5',
                                        width='50%',
                                        elevation=1)
        self.children = [self.options_container]
        
    def select_action(self, item, *args):
        if self.selected:
            self.options_dict[self.selected].deselect()
        
        self.selected = item.value
        item.select()
        
        


# ### Configuration

# In[93]:


class Canvas(v.Card):
    def __init__(self, x_label='Time', y_label='Amplitude', title='', *args, **kwargs):
        class_ = 'ma-2 pa-2'
        style_ = 'border-radius:20px'
        super().__init__(class_=class_,
                         style_=style_,
                         *args, **kwargs)
        
        self.canvas_title = v.CardTitle(children=[v.Spacer(), title, v.Spacer()], class_='pt-2 mt-1 pb-0 mb-0')

        figure = go.FigureWidget()
        figure.add_trace(go.Scatter(x=[], y=[], showlegend=False))
        figure.add_trace(go.Scatter(x=[], y=[], line=dict(color='rgba(0,121,96,0.7)', width=2, dash='dash'), showlegend=False))
        figure.update_layout(margin_l=70, margin_r=30, margin_t=10, margin_b=40, 
                             xaxis_title=x_label, yaxis_title=y_label)
        
        self.figure = figure
        
        self.children = [self.canvas_title, self.figure]
        
    def update_plot(self, x, y, z=[], name1='', name2='Setpoint'):
        self.figure.data[0]['x'] = x
        self.figure.data[0]['y'] = y
        self.figure.data[0]['name'] = name1
        if len(z):
            self.figure.data[1]['x'] = x
            self.figure.data[1]['y'] = z
            self.figure.data[1]['name'] = name2


# In[121]:


class CustomData(v.Card):
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)
        self.class_ = 'ma-2 pa-4'
        self.style_ = 'border-radius:20px'
        
        self.card_title = v.CardTitle(children=[v.Spacer(), 'Tuning Constraints', v.Spacer()], class_='py-2')
        # create the DataTable

        headers =  [
            { 'text': 'Constraint Name', 'value': 'name'},
            { 'text': 'Unit', 'value': 'unit'},
            { 'text': 'Lower', 'value': 'lower' },
            { 'text': 'Upper', 'value': 'upper' },
            { 'text': 'EU', 'value': 'val' },
        ]
        items = [
            # {
            #     'name': 'Proportional',
            #     'unit': '% / %',
            #     'lower': 0.0,
            #     'upper': 15.0,
            #     'val': 9.0,
            # },
            # {
            #     'name': 'Overshoot',
            #     'unit': '%',
            #     'lower': 9.0,
            #     'upper': 11.0,
            #     'val': 10.0,
            # }
        ]
        
        self.table = v.DataTable(headers=headers, 
                                 items=items,
                                 disable_filtering=True,
                                 disable_pagination=True,
                                 disable_sort=True,
                                 hide_default_footer=True,
                                 show_select=True,
                                 v_model=[],
                                 item_key='name',
                                 dense=True)
        
        # Create Select Option
        dropdown_items = ['Proportional', 'Integral', 'Overshoot', 'Settling Time']
        self.options_dropdown = v.Select(v_model=None, placeholder='Please Select ...', 
                                         items=dropdown_items, 
                                         color="#007960", 
                                         class_='ma-2 mb-0 pb-0',
                                         style_='font-size:10pt',
                                         dense=True)
        
        
        # Create Text Fields
        self.option_label = v.Text(children=[''], class_='mt-0 pt-0 mb-5 pr-4')
        self.value_field = v.TextField(label='value', placeholder='value', style_='max-width:70px; font-size:10pt', class_='mt-0 pt-1 pb-0 mx-1', color='#007960', dense=True, outlined=True)
        self.lb_field = v.TextField(label='lower', placeholder='-inf', style_='max-width:70px; font-size:10pt', class_='mt-0 pt-1 pb-0 mx-1', color='#007960', size=5, dense=True, outlined=True)
        self.ub_field = v.TextField(label='upper', placeholder='+inf', style_='max-width:70px; font-size:10pt', class_='mt-0 pt-1 pb-0 mx-1', color='#007960', dense=True, outlined=True)
        
        self.value_field.on_event('change', self.update_btns)
        self.lb_field.on_event('change', self.update_btns)
        self.ub_field.on_event('change', self.update_btns)

        self.unit_dict = {'Overshoot': '%', 'Settling Time': 'Min', 'Proportional': '% / %', 'Tau': 'Min', 'Integral': 'Min', 'Derivative': 'Min'}
        
        # Create Edit Buttons
        plus_icon = v.Icon(children='mdi-plus', small=False)
        self.plus_btn = v.Btn(children=[plus_icon],
                                color='success',
                                icon=True,
                                class_='mb-6',
                                disabled=True)
        
        check_icon = v.Icon(children='mdi-check', small=False)
        self.check_btn = v.Btn(children=[check_icon],
                                color='success',
                                icon=True,
                                class_='mb-6')
        
        minus_icon = v.Icon(children='mdi-minus', small=False)
        self.minus_btn = v.Btn(children=[minus_icon],
                                color='error',
                                icon=True,
                                class_='mb-6')
        
        edit_icon = v.Icon(children='mdi-pencil', small=False)
        self.edit_btn = v.Btn(children=[edit_icon],
                                color='cyan',
                                icon=True,
                                class_='mb-6')
        
        self.options_row = v.Row(children=[self.option_label, self.value_field, self.lb_field, self.ub_field, v.Spacer(), self.plus_btn, self.check_btn, self.minus_btn, self.edit_btn],
                                 class_='align-center justify-space-around mx-4 my-0 py-0',
                                 dense=True)
        # Hide btns at init.
        self.lb_field.hide()
        self.ub_field.hide()
        self.value_field.hide()
        self.edit_btn.hide()
        self.check_btn.hide()
        self.plus_btn.hide()
        self.minus_btn.hide()
        
        self.options_dropdown.on_event('change', self.select_action)
        self.plus_btn.on_event('click', self.add_item)
        self.minus_btn.on_event('click', self.remove_item)
        self.edit_btn.on_event('click', self.edit_item)
        
        self.children = [self.card_title, self.options_dropdown, self.options_row, self.table]

    def select_action(self, item, event, data):
        self.option_label.children = [item.v_model]
        self.ub_field.hide()
        
        if item.v_model in ['Overshoot', 'Settling Time'] :
            self.lb_field.v_model = None
            self.lb_field.hide()
            self.ub_field.v_model = None
            self.ub_field.hide()
            
            self.value_field.v_model = None
            self.value_field.show()
        else:
            self.lb_field.v_model = None
            self.lb_field.show()
            self.ub_field.v_model = None
            self.ub_field.show()
            
            self.value_field.v_model = None
            self.value_field.hide() 
        
        item.v_model = None
        
        self.plus_btn.show()
        self.check_btn.hide()
        self.update_btns()
        
        self.options_row.show()
        
    def add_item(self, *args):
        label = self.option_label.children[0]
        item = {   
            'name': label,
            'unit': self.unit_dict[label],
            'lower': self.lb_field.v_model,
            'upper': self.ub_field.v_model,
            'val': self.value_field.v_model,
        }
        
        self.table.items = self.table.items + [item]
        new_items = self.options_dropdown.items.copy()
        new_items.remove(label)
        self.options_dropdown.items = new_items
        
        self.option_label.children = ['']
        self.lb_field.hide()
        self.ub_field.hide()
        self.value_field.hide()
        self.plus_btn.disabled = True
        
        self.lb_field.v_model = ''
        self.ub_field.v_model = ''
        self.value_field.v_model = ''
        
        self.update_btns()
        
    def edit_item(self, item, *args):
        sel_item = self.table.v_model
        
        if len(sel_item) == 1:
            sel = sel_item[0]
            self.option_label.children = [sel['name']]
            if sel['name'] in ['Overshoot', 'Settling Time'] :
                self.lb_field.v_model = None
                self.lb_field.hide()
                self.ub_field.v_model = None
                self.ub_field.hide()

                self.value_field.show()
                
                self.value_field.v_model = sel['val']
            else:
                self.lb_field.v_model = sel['lower']
                self.lb_field.show()
                self.ub_field.v_model = sel['upper']
                self.ub_field.show()

                self.value_field.v_model = None
                self.value_field.hide() 
            
            self.plus_btn.hide()
            self.check_btn.show()
            self.update_btns()

            self.options_row.show()
            
        
    def remove_item(self, *args):
        items = self.table.v_model
        labels = [item_i['name'] for item_i in items]
        
        new_items = self.table.items.copy()
        for item_i in items.copy():
            new_items.remove(item_i)
        self.table.items = new_items
        
        self.options_dropdown.items = self.options_dropdown.items + labels
        self.table.v_model = []
        
        self.lb_field.v_model = ''
        self.ub_field.v_model = ''
        self.value_field.v_model = ''
        
        self.update_btns()
                
        # if (self.value_field.v_model) or (self.lb_field.v_model) or (self.ub_field.v_model):
            
    
    def update_btns(self, *args):
        if (self.value_field.v_model) or (self.lb_field.v_model) or (self.ub_field.v_model):
            self.plus_btn.disabled = False
        else:
            self.plus_btn.disabled = True

        data = self.table.items
        
        if len(data) > 0:
            self.minus_btn.show()
            self.edit_btn.show()
        else:
            self.minus_btn.hide()
            self.edit_btn.hide()


# In[113]:


class CustomSlider(v.Row):
    def __init__(self, val, min_, max_, unit_text='', font_size='10.5pt'):
        super().__init__(class_='d-flex flex-row mx-4 my-0 py-0 align-center justify-center', dense=True)
        
        self.default_min = min_
        self.default_max = max_
        self.default_val = val
        
        self.slider = v.Slider(v_model=val, min=min_, max=max_, 
                               thumb_label=False, thumb_size=30, thumb_color='#007960', 
                               track_fill_color='#007960', 
                               step=0.01, 
                               track_color='#f5f5f5', 
                               # class_='d-flex my-0 py-0 pt-1 justify-start',
                               class_='d-flex justify-start',
                               height='30px', loader_height='1px',
                               style_='min-width:30px',
                               dense=True)
        
        self.slider_textfield = v.TextField(v_model=self.slider.v_model, 
                                    dense=True, solo=True, 
                                    shadow=1, flat=True, 
                                    class_='d-flex ml-1 my-0 py-0 mr-0 pr-0 justify-start', 
                                    filled=True, background_color='#f5f5f5',
                                    height='1px',
                                    style_='max-width:65px; font-size:10pt; height:55px')
        self.slider_textfield.kwargs = {'slider_check': self.slider_check}
        self.slider.observe(self.slider_sync)
        # self.slider.on_event('change', self.slider_action)

        # self.slider_textfield.on_event('change', self.slider_check)

        self.unit_text = v.Text(children=[unit_text],
                                class_='d-flex flex-row align-center justify-end pl-2 pb-3 pr-0 mr-0',
                                style_='font-size:{}'.format(font_size))
        
        self.children = [self.slider, self.slider_textfield, self.unit_text]
        
    def slider_sync(self, item, *args):
        self.slider_textfield.v_model = item['owner'].v_model
    
    def slider_check(self, item):
        try:
            val = float(item)
        except:
            self.slider_textfield.v_model = self.default_val
            val = self.slider_textfield.v_model
        if val > self.slider.max:
            self.slider.max = val + 0.1*abs(val)
        elif val < self.slider.min:
            self.slider.min = val - 0.1*abs(val)
        else:
            self.slider.min = self.default_min
            self.slider.max = self.default_max

        if val != self.slider.v_model:
            self.slider.v_model = val
            return 1
        return 0
        
        
    def slider_action(self, *args):
        pass
    
    def set_limits(self, min_, max_, val):
        self.default_min = min_
        self.default_max = max_
        self.default_val = val
        
        self.slider.min = self.default_min
        self.slider.max = self.default_max
        self.slider.v_model = val


class PIDCard(v.Card):
    def __init__(self, **kwargs):
        class_='ma-2 pa-2 pr-0'
        style_='border-radius:20px'
        super().__init__(class_=class_,
                         style_=style_,
                         **kwargs)
        
        self.controller_title = v.CardTitle(children=[v.Spacer(), 'Controller Parameters', v.Spacer()], class_='py-2')
        
        self.p_label = v.Text(children=[
                                        'Proportional', 
                                        # ' (',
                                        # create_eq('$K_c$', 'b', 2, top='0'), 
                                        # ' )'
                                       ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2')
        
        self.i_label = v.Text(children=[
                                        'Integral',
                                        # ' (',
                                        # create_eq('$ \\tau_I $', 'b', 2.5, top='0'),
                                        # ' )'
                                       ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2')
        
        self.d_label = v.Text(children=[
                                        'Derivative',
                                        # ' (',
                              # create_eq('$ \\tau_D $', 'b', 2.5, top='0'),
                                        # ' )'
                                       ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2')
        
        self.labels = v.Card(children=[self.p_label, self.i_label, self.d_label], style_='width:100px', elevation=0, class_='pl-3')
        
        self.p_slider = CustomSlider(10, -20, 20, '%/%', '9.3pt')
        self.i_slider = CustomSlider(5, 0, 100, ' Min')
        self.d_slider = CustomSlider(0, 0, 20, ' Min')
        
        self.sliders = v.Card(children=[self.p_slider, self.i_slider, self.d_slider], style_='min-width:165px; width:250px; background-color: rgba(255, 255, 255, 0.0)', elevation=0)
        
        content = v.CardActions(children=[self.labels, self.sliders], class_='ma-0 pa-0 px-1', style_='background-color: rgba(255, 255, 255, 0.5)')
        
        
        
        self.children = [self.controller_title, content]
        


# In[115]:


class ModelParamCard(v.Card):
    def __init__(self, **kwargs):
        class_='ma-2 pa-2 pr-0'
        style_='border-radius:20px'
        super().__init__(class_=class_,
                         style_=style_,
                         **kwargs)
        
        self.plant_param_title = v.CardTitle(children=[v.Spacer(), 'Plant Parameters', v.Spacer()], class_='py-2')
        
        self.g_label = v.Text(children=[
                                        'Gain',
                                        # ' (',
                                        # create_eq('$K_p$', 'b', 2, top='0'), 
                                        # ' )'
                                       ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2')
        
        self.tau_label = v.Text(children=[
                                        'Time-constant', 
                                        # ' (',
                                        # create_eq('$ \\tau_p $', 'b', 2.5, top='0'),
                                        # ' )'
                                         ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2',
                              style_='font-size:9.5pt')
        
        self.d_label = v.Text(children=[
                                        'Dead-time',
                                        # ' (',
                                        # create_eq('$ \\theta_p $', 'b', 2.5, top='0'),
                                        # ' )'
                                       ],
                              class_='d-flex flex-row align-center justify-start pb-3 mb-3 py-2')
        
        self.labels = v.Card(children=[self.g_label, self.tau_label, self.d_label], style_='max-width:100px', elevation=0, class_='pl-3')

        self.g_slider = CustomSlider(10, -20, 20, '%/%', '9.3pt')
        self.tau_slider = CustomSlider(5, 0, 100, 'Min')
        self.d_slider = CustomSlider(0, 0, 20, 'Min')
        
        self.sliders = v.Card(children=[self.g_slider, self.tau_slider, self.d_slider], style_='min-width:150px; width:250px', elevation=0)
        
        content = v.CardActions(children=[self.labels, self.sliders], class_='ma-0 pa-0 px-1', color='none')
        
        self.children = [self.plant_param_title, content]
        

class MethodCard(v.Card):
    def __init__(self, *args, **kwargs):
        class_ = 'ma-2 pa-2 px-6'
        style_ = 'border-radius:20px'
        super().__init__(class_=class_,
                         style_=style_,
                         *args, **kwargs)
        
        self.card_title = v.CardTitle(children=[v.Spacer(),'Tuning Methods', v.Spacer()],
                                      class_='py-2')
        
        self.methods = {
            'Optimization-based': ['ISE', 'IAE', 'ITSE'],
            'Rule-based': ['IMC', 'Ziegler-Nichols', 'Cohen-Coon', 'Kappa-Tau', 'Lambda'],
            'Tau-based': [],
            'Custom': []
        }
        
        radio_list = []
        for method_i in self.methods.keys():
            radio_i = v.Radio(label=method_i, value=method_i, color='#007960', dense=True)
            radio_list += [radio_i]
            
        self.method_radio = v.RadioGroup(v_model='Optimization-based', children=radio_list, dense=True, class_='mt-1 pt-1')
        self.method_select = v.Select(items=self.methods[self.method_radio.v_model],
                                      v_model=self.methods[self.method_radio.v_model][0],
                                      color='#007960', item_color='#007960', dense=True)
        self.cl_tau = v.TextField(label='Tau',
                                  v_model='',
                                  dense=True, solo=True, 
                                  outlined=True,
                                  shadow=1, flat=True, 
                                  shaped=False,
                                  class_='d-flex ml-1 pl-3 mt-3 pr-3 justify-center align-end', 
                                  filled=True, background_color='#f5f5f5', 
                                  height='1px',
                                  color='#007960',
                                  style_='max-width:87px; font-size:10pt; height:55px',
                                  disabled=True)
        self.imc_mode_select = v.Select(items=['Conservative', 'Moderate', 'Aggresive'],
                                        v_model='Moderate',
                                        filled=True,
                                        outlined=True,
                                        color='#007960', item_color='#007960', dense=True,
                                        style_='max-width:150px; font-size:12pt; color: black')
        self.imc_mode_select.hide()
        
        self.cl_tau_tt = add_tooltip(self.cl_tau, 'Closed Loop Time Constant')
        
        self.selected_cache = {}
        self.selected_method_cache = 'Optimization-based'
        for method_i in self.methods:
            if len(self.methods[method_i]) > 0:
                self.selected_cache[method_i] = self.methods[method_i][0]
            else:
                self.selected_cache[method_i] = ''
        
        self.method_radio.on_event('change', self.method_radio_action)
        self.method_select.on_event('change', self.method_select_action)
        
        self.special_options = v.Row(children=[self.method_radio, v.Spacer(), self.imc_mode_select, self.cl_tau_tt])
        
        self.children = [self.card_title, self.special_options, self.method_select]
        
    
    def method_radio_action(self, item, *args):
        self.selected_cache[self.selected_method_cache] = self.method_select.v_model

        # self.selected_cache[item.v_model] = selected_cache_new
        self.method_select.v_model = self.selected_cache[item.v_model]
        self.method_select.items = self.methods[item.v_model]
        self.selected_method_cache = item.v_model
        
        if item.v_model == 'Tau-based':
            self.method_select.hide()
            self.imc_mode_select.hide()
            self.cl_tau.disabled = False
        elif item.v_model == 'Custom':
            self.method_select.hide()
            self.imc_mode_select.hide()
            self.cl_tau.disabled = True
        elif item.v_model == 'Optimization-based':
            self.imc_mode_select.hide()
            self.cl_tau.disabled = True
            self.method_select.show()
        else:
            self.method_select.show()
            if self.method_select.v_model == 'IMC':
                self.imc_mode_select.show()
                self.cl_tau.disabled = False
            else:
                self.cl_tau.disabled = True
                self.imc_mode_select.hide()
        
    def method_select_action(self, item, *args):
        if item.v_model == 'IMC':
            self.cl_tau.disabled = False
            self.imc_mode_select.show()
        else:
            self.cl_tau.disabled = True
            self.imc_mode_select.hide()
            


class SimCard(v.Card):
    def __init__(self, **kwargs):
        class_='ma-2 pa-2 pr-0'
        style_='border-radius:20px; min-width:300px'
        super().__init__(class_=class_,
                         style_=style_,
                         **kwargs)
        
        self.simulation_title = v.CardTitle(children=[v.Spacer(), 'Simulation Options', v.Spacer()], class_='py-2')
        
        self.sim_time_label = v.Text(children=['Simulation Time'])
        self.sp_label = v.Text(children=['Setpoint'])
        self.dist_label = v.Text(children=['Disturbance'])
        
        self.sim_time_textbox = v.TextField(v_model='60',
                                            dense=True, solo=True, 
                                            outlined=True,
                                            shadow=1, flat=True, 
                                            shaped=False,
                                            class_='d-flex ml-1 my-0 py-0 mr-0 pr-3 justify-center align-end', 
                                            filled=True, background_color='#f5f5f5', 
                                            height='1px',
                                            color='#007960',
                                            style_='max-width:75px; font-size:10pt; height:55px')
        
        self.sp_textbox = v.TextField(v_model='1',
                                      dense=True, solo=True, 
                                      outlined=True,
                                      shadow=1, flat=True, 
                                      shaped=False,
                                      class_='d-flex ml-1 my-0 py-0 mr-0 pr-6 justify-center align-end', 
                                      filled=True, background_color='#f5f5f5', 
                                      height='1px',
                                      color='#007960',
                                      style_='max-width:87px; font-size:10pt; height:55px')
        
        self.dist_textbox = v.TextField(v_model='0',
                                        dense=True, solo=True, 
                                        outlined=True,
                                        shadow=1, flat=True, 
                                        shaped=False,
                                        class_='d-flex ml-1 my-0 py-0 mr-0 pr-6 justify-center align-end', 
                                        filled=True, background_color='#f5f5f5', 
                                        height='1px',
                                        color='#007960',
                                        style_='max-width:87px; font-size:10pt; height:55px')
        
        self.sim_time_unit = v.Text(children=['Min'], class_='ma-0 pa-0')
        self.sp_unit = v.Text(children=['[-]'])
        self.dist_unit = v.Text(children=['[-]'])
        
        self.sim_time_row = v.Row(children=[self.sim_time_label, v.Spacer(), self.sim_time_textbox, self.sim_time_unit], class_='pa-0 ma-0 px-2 mx-2 pt-3')
        self.sp_row = v.Row(children=[self.sp_label, v.Spacer(), self.sp_textbox, self.sp_unit], class_='pa-0 ma-0 px-2 mx-2')
        self.dist_row = v.Row(children=[self.dist_label, v.Spacer(), self.dist_textbox, self.dist_unit], class_='pa-0 ma-0 px-2 mx-2')
        
        self.content = v.Container(children=[self.sim_time_row, self.sp_row, self.dist_row])
        
        
        self.children = [self.simulation_title, self.sim_time_row, self.sp_row, self.dist_row]


# In[126]:


# table_card = v.Card(children=[CustomData()], class_='ma-2 pa-4', style_='border-radius:20px')
class TuningPage(v.Card):
    def __init__(self, *args, **kwargs):
        class_='ma-1 pa-1'
        color='#007960'
        style_='border-radius:20px; min-width:98%'
        
        super().__init__(class_=class_,
                         color=color,
                         style_=style_)
        
        self.constraints_card = CustomData(width='34.5%')
        self.op_card = Canvas(title='OP', width='31%')
        self.pv_card = Canvas(title='PV', width='31.5%')
        
        self.method_card = MethodCard(width='34.5%')
        self.pid_card = PIDCard(width='22%')
        self.model_card = ModelParamCard(width='22%')
        self.sim_card = SimCard()

        row_1 = v.Container(children=[self.constraints_card, self.op_card, self.pv_card], class_='d-flex flew-row justify-start pb-0', elevation=0)
        row_2 = v.Container(children=[self.method_card, self.pid_card, self.model_card, self.sim_card], class_='d-flex flew-row pt-0', elevation=0, style_='', color='#007960')
        
        self.children = [row_1, row_2]

