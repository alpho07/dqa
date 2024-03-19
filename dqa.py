import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import os
import warnings
import geopandas as gpd
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_extras.dataframe_explorer import dataframe_explorer
import streamlit_highcharts as hct
import plotly.graph_objects as go

warnings.filterwarnings('ignore')

st.set_page_config(page_title='National DQA', page_icon=":bar_chart", layout="wide", initial_sidebar_state="auto",
                   menu_items=None)
st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
# st.title('DQA Dashboard')

os.chdir(r"C:\Users\ALPHY\Desktop\StreamLitDashboard")
df_assessments = pd.read_csv('dqa_assessments.csv', encoding='ISO-8859-1')
df_systems_assessment = pd.read_csv('dqa_system_assessment.csv', encoding='ISO-8859-1')

logo_path = "edqa.png"

# Display the logo at the top of the sidebar
st.sidebar.image(logo_path, width=200)

with st.sidebar:
    selected = option_menu("Main Menu",
                           ["Home", "System Assessment", 'Data Verification', 'Data Completeness', 'Service QA'],
                           icons=['house'], menu_icon="cast", default_index=1)
    st.markdown(
        """
        <style>
           .eczjsme4{
           padding-top: 2rem;

           }
        </style>
        """,
        unsafe_allow_html=True
    )
    selected


@st.cache_data
def filter_dataframe(df, selected_year, selected_level, selected_period):
    if selected == 'System Assessment' or selected == 'Data Verification' or selected == 'Data Completeness' or selected == 'Service QA':
        filtered_df = df_systems_assessment.copy()
    elif selected == 'Home':
        filtered_df = df_assessments.copy()
    if selected_year:
        selected_year = sorted(selected_year)
        filtered_df = filtered_df[filtered_df['year'].isin(selected_year)]
    if selected_level:
        filtered_df = filtered_df[filtered_df['level'].isin(selected_level)]
    if selected_period:
        filtered_df = filtered_df[filtered_df['month_year'].isin(selected_period)]
    return filtered_df


if selected == 'System Assessment' or selected == 'Data Verification' or selected == 'Data Completeness' or selected == 'Service QA':
    filcol1, filcol2, filcol3, filcol4 = st.columns(4)
    with filcol1:
        selected_year = st.multiselect('DQA Year', sorted(df_systems_assessment['year'].unique()))
    with filcol2:
        filtered_df = filter_dataframe(df_systems_assessment, selected_year, [], [])
        selected_level = st.multiselect('DQA Level', filtered_df['level'].unique())
    with filcol3:
        filtered_df = filter_dataframe(df_systems_assessment, selected_year, selected_level, [])
        selected_period = st.multiselect('DQA Period', filtered_df['month_year'].unique())
    with filcol4:
        filtered_df = filter_dataframe(df_systems_assessment, selected_year, selected_level, selected_period)
        selected_assessment = st.multiselect('DQA Assessment', filtered_df['assessment'].unique())


elif selected == 'Home':
    hcol1, hcol2, hcol3, hcol4 = st.columns(4)
    with hcol1:
        selected_year = st.multiselect('DQA Year', sorted(df_assessments['year'].unique()))

    with hcol2:
        # Filter DataFrame based on selected_year
        filtered_df = filter_dataframe(df_assessments, selected_year, [], [])
        selected_level = st.multiselect('DQA Level', filtered_df['level'].unique())

    with hcol3:
        # Filter DataFrame based on selected_year and selected_level
        filtered_df = filter_dataframe(df_assessments, selected_year, selected_level, [])
        selected_period = st.multiselect('DQA Period', filtered_df['month_year'].unique())

    with hcol4:
        # Filter DataFrame based on selected_year, selected_level, and selected_period
        filtered_df = filter_dataframe(df_assessments, selected_year, selected_level, selected_period)
        selected_assessment = st.multiselect('DQA Assessment', filtered_df['assessment'].unique())

    # Display the final DataFrame

    dcol1, dcol2 = st.columns([2, 1])
    with dcol1:
        colored_header(
            label="DQA Counties",
            description="Map with counties and number of DQAs done",
            color_name="violet-70",
        )

        df1 = filtered_df.groupby('county').agg({'value': 'sum'}).reset_index()
        kenya_counties_geojson = "County1.json"  # Replace with the actual path to your GeoJSON file

        # Read GeoJSON file using GeoPandas
        gdf = gpd.read_file(kenya_counties_geojson)

        # Merge the data into the GeoDataFrame
        gdf = gdf.merge(df1, left_on='COUNTY', right_on='county')

        # Calculate the centroid of the GeoDataFrame
        centroid = gdf.geometry.centroid

        # Create a Plotly figure from the GeoDataFrame
        fig = px.choropleth_mapbox(gdf,
                                   geojson=gdf.geometry,
                                   locations=gdf.index,
                                   color="value",  # Use the 'Value' column for coloring
                                   mapbox_style="stamen-toner",
                                   # color_continuous_scale="Viridis",
                                   # animation_frame='value',
                                   hover_name="county",
                                   center={"lat": centroid.y.mean(), "lon": centroid.x.mean()},
                                   # Adjust the center as needed
                                   zoom=5, height=650, hover_data={"county": True, "value": True})

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 150, "t": 0, "l": 0, "b": 0}, )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Data"):
        st.write('')
        # filtered_df1 = dataframe_explorer(filtered_df, case=False)
        # st.dataframe(filtered_df1)

    with dcol2:
        colored_header(
            label="DQA Uptake",
            description="This gives number of DQAs done at each level",
            color_name="violet-70",
        )

        national = filtered_df[filtered_df['level'] == 'National'].groupby('year')[
            'level'].nunique().reset_index()
        county = filtered_df[filtered_df['level'] == 'County'].groupby('year')['county'].nunique().reset_index()
        sub_county = filtered_df[filtered_df['level'] == 'Sub County'].groupby('year')[
            'level'].nunique().reset_index()
        agency = filtered_df[filtered_df['level'] == 'Agency'].groupby('year')['level'].nunique().reset_index()
        partners = filtered_df[filtered_df['level'] == 'Partners'].groupby('year')[
            'level'].nunique().reset_index()

        dc1, dc2, dc3 = st.columns(3)
        dc1.metric(label="National", value=national.shape[0])
        dc2.metric(label="Participants", value=national.shape[0])
        dc3.metric(label="National", value=national.shape[0])

        dcol2.metric(label="National", value=national.shape[0])
        dcol2.metric(label="County", value=county.shape[0])
        dcol2.metric(label="Sub-County", value=sub_county.shape[0])
        dcol2.metric(label="Agency", value=agency.shape[0])
        dcol2.metric(label="Partners", value=partners.shape[0])
        style_metric_cards(
            background_color="#fff",
            border_size_px=1,
            border_color="#CCC",
            border_radius_px=5,
            border_left_color="#9AD8E1",
            box_shadow=True,
        )

if selected == 'System Assessment':
    # os.chdir(r"C:\Users\ALPHY\Desktop\StreamLitDashboard")
    df_assessment = filtered_df  # pd.read_csv('dqa_system_assessment.csv', encoding='ISO-8859-1')
    # df_assessment1 = df_assessment[df_assessment['assessment'].isin(['2021 National HIV DQA'])]

    system_assessment, composite_score = st.tabs(["SYSTEM ASSESSMENT", '_'])
    with system_assessment:
        # st.header('System Assessment')
        overall, mne_functions, data_management, data_collection, emr_systems = st.tabs(
            ['OVERALL', 'M&E FUNCTIONS', 'DATA MANAGEMENT', 'DATA COLLECTION', 'EMR SYSTEMS'])
        with overall:
            # national_performance, county_performance, facility_performance = st.columns(3)
            # with national_performance:
            #    st.title('National Performance')
            # with county_performance:
            #    st.title('County Performance')
            # with facility_performance:
            #    st.title('Facility Performance')
            system_overall, system_per_section = st.columns([1, 1])
            with system_overall:
                grouped_data = df_assessment.groupby('section')['score'].sum().reset_index()
                total_value_sum = df_assessment['score'].sum()
                grouped_data['percentage'] = (grouped_data['score'] / total_value_sum) * 100

                fig = px.line_polar(grouped_data, r='percentage', theta='section',
                                    line_close=True, title='System Assessment Overall Score',
                                    width=800, height=400)
                st.plotly_chart(fig, use_container_width=True)
                # st.dataframe(grouped_data)
            with system_per_section:
                filtered_data1 = df_assessment[df_assessment['response'].isin(['Yes', 'Partly', 'No'])]

                # Group by 'section' and 'optionItemName' and sum the 'score' column
                grouped_data = filtered_data1.groupby(['section', 'response'])['score'].sum().reset_index()

                # Calculate the total percentage for each section
                grouped_data['total_percentage'] = grouped_data.groupby('section')['score'].transform('sum')

                # Calculate the percentage for each optionItemName in each section
                grouped_data['percentage'] = (grouped_data['score'] / grouped_data['total_percentage']) * 100

                color_map = {'Yes': 'green', 'Partly': 'yellow', 'No': 'red'}

                # Add hover_data and hovertemplate for formatted percentage labels
                fig = px.bar(grouped_data, x='percentage', y='section', color='response',
                             color_discrete_map=color_map, text='percentage',
                             hover_data=['percentage'],  # Include this line for hover data
                             title='System Assessment Score Per Section',
                             labels={'percentage': 'Percentage', 'section': 'Section'},
                             width=800, height=500)

                # Use hovertemplate for formatting the percentage labels
                fig.update_traces(hovertemplate='%{text:.2f}%', texttemplate='%{text:.2f}%', textposition='inside')

                # Adjust the layout for better visibility of chat labels
                fig.update_layout(legend=dict(title_text='Option',
                                              orientation="h",
                                              yanchor="bottom",
                                              y=-0.15,
                                              xanchor="center",
                                              x=0.5),
                                  yaxis_title='Section',
                                  xaxis_title='Percentage',
                                  barmode='stack',
                                  bargap=0.5,
                                  showlegend=True,

                                  )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

        with mne_functions:
            mn1, mn2 = st.columns([1, 1])
            with mn1:
                mne1 = df_assessment[df_assessment['identifier'].isin(['Staff M&E Training'])]
                new_df = mne1.groupby(['category', 'question'])['value'].sum().reset_index()
                category_order = ['HTS', 'PMTCT', 'C&T', 'Overall']
                # Order the DataFrame by 'category' column
                new_df['category'] = pd.Categorical(new_df['category'], categories=category_order, ordered=True)
                new_df_ = new_df.sort_values('category')
                categories = new_df_['category'].unique()
                values1 = \
                    new_df[new_df_['question'] == 'Number of staff resposible for data management'].groupby('category')[
                        'value'].sum()
                values2 = new_df[new_df_['question'] == 'Staff trained on M&E Tools'].groupby('category')['value'].sum()

                # Calculate percentages for the line
                percentages = [(v2 / v1) * 100 for v1, v2 in zip(values1, values2)]

                # Define colors for the bar traces
                color1 = 'rgba(55, 128, 191, 0.7)'  # Blue
                color2 = 'rgba(219, 64, 82, 0.7)'  # Red

                # Create bar traces with different colors
                trace1 = go.Bar(x=categories, y=values1, name='Number of staff resposible for data management',
                                text=values1, textposition='inside', )
                trace2 = go.Bar(x=categories, y=values2, name='Staff trained on M&E Tools', text=values2,
                                textposition='inside')

                formatted_percentages = [f'{p:.2f}' for p in percentages]

                # Create line trace
                trace_line = go.Scatter(x=categories, y=formatted_percentages, mode='lines+markers', yaxis='y2',
                                        name='Percentage Line', text=formatted_percentages,  # Custom text for markers
                                        hoverinfo='x+y+text', )

                # Create layout
                layout = go.Layout(title='Staff M&E training',
                                   height=600,
                                   width=400,
                                   yaxis=dict(title='Values'),
                                   yaxis2=dict(title='Percentage', overlaying='y', side='right', range=[0, 100]),
                                   barmode='group',  # Corrected value
                                   legend=dict(x=00, y=-0.15, orientation='h'))  # Move legend to center bottom

                # Create figure
                fig = go.Figure(data=[trace1, trace2, trace_line], layout=layout)
                # Show the plot
                st.plotly_chart(fig, use_container_width=True)

            with mn2:
                # mne11,mne22 =  st.tabs([''])
                mne2 = df_assessment[df_assessment['questionId'].isin([1])]
                filtered_data1 = df_assessment[df_assessment['response'].isin(['Yes', 'Partly', 'No'])]

                # Group by 'section' and 'optionItemName' and sum the 'score' column
                grouped_data = filtered_data1.groupby(['response'])['value'].sum().reset_index()

                # Calculate the total score for normalization
                total_score = grouped_data['value'].sum()

                # Convert 'total_score' to numeric in case it's a string
                total_score = pd.to_numeric(total_score, errors='coerce')

                # Calculate the percentage for each optionItemName
                grouped_data['percentage'] = (grouped_data['value'] / total_score) * 100

                custom_colors = ['#008000', '#FFFF00', '#FF0000']

                # Draw a donut chart using Plotly
                fig = px.pie(grouped_data, names='response', values='percentage',
                             hole=0.5,  # Set the size of the hole for the donut chart
                             title='Documentation of Staff roles and Responsibilities in data Management',
                             labels={'percentage': 'Percentage', 'response': 'Response'},
                             color_discrete_sequence=custom_colors)

                # Set the legend position to bottom
                fig.update_layout(legend=dict(x=0.3, y=-0.14, orientation='h'))
                fig.update_layout(height=350, width=350)
                fig.update_traces(hovertemplate='%{percent:%}')
                fig.update_traces(textfont_size=20)  # Adjust the text size
                st.plotly_chart(fig, use_container_width=True)

                # Second chart starts here
                mne22 = df_assessment[df_assessment['questionId'].isin([101])]
                filtered_data2 = mne22[mne22['response'].isin(['Yes', 'No'])]

                # Group by 'section' and 'optionItemName' and sum the 'score' column
                grouped_data1 = filtered_data2.groupby(['response'])['value'].sum().reset_index()

                # Calculate the total score for normalization
                total_score1 = grouped_data1['value'].sum()

                # Convert 'total_score' to numeric in case it's a string
                total_score1 = pd.to_numeric(total_score1, errors='coerce')

                # Calculate the percentage for each optionItemName
                grouped_data1['percentage'] = (grouped_data1['value'] / total_score1) * 100

                custom_colors1 = ['#008000', '#FFFF00', '#FF0000']

                # Draw a donut chart using Plotly
                fig = px.pie(grouped_data1, names='response', values='percentage',
                             hole=0,  # Set the size of the hole for the donut chart
                             title='Orientation package for new staff',
                             labels={'percentage': 'Percentage', 'response': 'Response'},
                             color_discrete_sequence=custom_colors1)

                # Set the legend position to bottom
                fig.update_layout(legend=dict(x=0.3, y=-0.14, orientation='h'))
                fig.update_layout(height=350, width=350)
                fig.update_traces(hovertemplate='%{percent:%}')
                fig.update_traces(textfont_size=20)  # Adjust the text size
                st.plotly_chart(fig, use_container_width=True)

        with data_management:
            data_management_df = df_assessment[df_assessment['identifier'].isin(['Data Management Processes'])]

            # Group by 'questionName' and 'optionItemName' and sum the 'value' column
            data_management_df_grouped = data_management_df.groupby(['question', 'response'])[
                'score'].sum().reset_index()

            # Calculate the total percentage for each section
            data_management_df_grouped['total_percentage'] = data_management_df_grouped.groupby('question')[
                'score'].transform('sum')

            # Calculate the percentage for each optionItemName in each section
            data_management_df_grouped['percentage'] = (data_management_df_grouped['score'] /
                                                        data_management_df_grouped['total_percentage']) * 100

            color_map = {'Yes': 'green', 'Partly': 'yellow', 'No': 'red'}

            # Reorder the response categories
            data_management_df_grouped['response'] = pd.Categorical(data_management_df_grouped['response'],
                                                                    categories=['Yes', 'Partly', 'No'], ordered=True)

            # Add hover_data and hovertemplate for formatted percentage labels
            fig = px.bar(data_management_df_grouped, x='percentage', y='question', color='response',
                         color_discrete_map=color_map, text='percentage',
                         hover_data=['percentage'],  # Include this line for hover data
                         title='System Assessment Score Per Section',
                         labels={'percentage': 'Percentage', 'question': 'Section'},
                         width=800, height=500)

            # Use hovertemplate for formatting the percentage labels
            fig.update_traces(hovertemplate='%{text:.2f}%', texttemplate='%{text:.2f}%', textposition='inside')

            # Adjust the layout for better visibility of chat labels
            fig.update_layout(legend=dict(title_text='Option',
                                          orientation="h",
                                          yanchor="bottom",
                                          y=-0.15,
                                          xanchor="center",
                                          x=0.5),
                              yaxis_title='Section',
                              xaxis_title='Percentage',
                              barmode='stack',
                              bargap=0.5,
                              showlegend=True
                              )
            st.plotly_chart(fig, use_container_width=True)

        with data_collection:
            tools, registers = st.tabs(['Collection Tools', 'Registers'])
            with tools:
                data_management_df = df_assessment[df_assessment['response'].isin(['Available', 'In Use'])]
                new_df = df_assessment.groupby(['question', 'response'])['value'].sum().reset_index()
                category_order = ['MOH 333', 'MOH 362', 'MOH 366', 'MOH 405', 'MOH 406', 'MOH 408', 'MOH 729B',
                                  'MOH 730B',
                                  'MOH 731']
                # Order the DataFrame by 'category' column
                new_df['question'] = pd.Categorical(new_df['question'], categories=category_order, ordered=True)
                new_df_ = new_df.sort_values('question')

                categories = new_df_['question'].unique()
                values1 = new_df[new_df_['response'] == 'Available'].groupby('question')['value'].sum()
                values2 = new_df[new_df_['response'] == 'In Use'].groupby('question')['value'].sum()

                # Calculate percentages for the line
                percentages = [(v2 / v1) * 100 for v1, v2 in zip(values1, values2)]

                # Define colors for the bar traces
                color1 = 'rgba(55, 128, 191, 0.7)'  # Blue
                color2 = 'rgba(219, 64, 82, 0.7)'  # Red

                # Create bar traces with different colors
                trace1 = go.Bar(x=categories, y=values1, name='Available', text=values1, textposition='inside', )
                trace2 = go.Bar(x=categories, y=values2, name='In Use', text=values2, textposition='inside')

                formatted_percentages = [f'{p:.2f}' for p in percentages]

                # Create line trace
                trace_line = go.Scatter(x=categories, y=formatted_percentages, mode='lines+markers', yaxis='y2',
                                        name='Percentage Line', text=formatted_percentages,  # Custom text for markers
                                        hoverinfo='x+y+text', )

                # Create layout
                layout = go.Layout(title='Tools available and Use',
                                   yaxis=dict(title='Values'),
                                   yaxis2=dict(title='Percentage', overlaying='y', side='right', range=[0, 100]),
                                   barmode='group',  # Corrected value
                                   legend=dict(x=00, y=-0.15, orientation='h'))  # Move legend to center bottom
                # Create figure
                fig = go.Figure(data=[trace1, trace2, trace_line], layout=layout)
                # Show the plot
                st.plotly_chart(fig, use_container_width=True)
            with registers:
                inventory, file_storage = st.columns([1, 1])
                with inventory:
                    dataset1 = df_assessment[df_assessment['questionId'] == 22]
                    filtered_data1 = dataset1[dataset1['response'].isin(['Yes', 'Partly', 'No'])]

                    # Group by 'section' and 'optionItemName' and sum the 'score' column
                    grouped_data = filtered_data1.groupby(['response'])['value'].sum().reset_index()

                    # Calculate the total score for normalization
                    total_score = grouped_data['value'].sum()

                    # Convert 'total_score' to numeric in case it's a string
                    total_score = pd.to_numeric(total_score, errors='coerce')

                    # Calculate the percentage for each optionItemName
                    grouped_data['percentage'] = (grouped_data['value'] / total_score) * 100

                    custom_colors = ['#008000', '#FFFF00', '#FF0000']
                    grouped_data['label'] = df_assessment['response']

                    # Draw a donut chart using Plotly
                    fig = px.pie(grouped_data, names='response', values='percentage',
                                 hole=0.5,  # Set the size of the hole for the donut chart
                                 title='Inventory of HTS Registers by Service delivery Points available',
                                 labels={'percentage': 'Percentage', 'response': 'Response'},
                                 color_discrete_sequence=custom_colors)

                    # Set the legend position to bottom
                    fig.update_layout(legend=dict(x=0.3, y=-0.14, orientation='h'))
                    fig.update_traces(hovertemplate='<b>%{label}</b>: %{percent:%}')
                    fig.update_traces(textfont_size=20)  # Adjust the text size
                    st.plotly_chart(fig, use_container_width=True)
                with file_storage:
                    dataset1 = df_assessment[df_assessment['questionId'] == 23]
                    filtered_data1 = dataset1[dataset1['response'].isin(['Yes', 'Partly', 'No'])]

                    # Group by 'section' and 'optionItemName' and sum the 'score' column
                    grouped_data = filtered_data1.groupby(['response'])['value'].sum().reset_index()

                    # Calculate the total score for normalization
                    total_score = grouped_data['value'].sum()

                    # Convert 'total_score' to numeric in case it's a string
                    total_score = pd.to_numeric(total_score, errors='coerce')

                    # Calculate the percentage for each optionItemName
                    grouped_data['percentage'] = (grouped_data['value'] / total_score) * 100

                    custom_colors = ['#008000', '#FFFF00', '#FF0000']
                    grouped_data['label'] = df_assessment['response']

                    # Draw a donut chart using Plotly
                    fig = px.pie(grouped_data, names='response', values='percentage',
                                 hole=0.0,  # Set the size of the hole for the donut chart
                                 title='File storage: Arranged in chronological manner & in a secure location',
                                 labels={'percentage': 'Percentage', 'response': 'Response'},
                                 color_discrete_sequence=custom_colors)

                    # Set the legend position to bottom
                    fig.update_layout(legend=dict(x=0.3, y=-0.14, orientation='h'))
                    fig.update_traces(hovertemplate='<b>%{label}</b>: %{percent:%}')
                    fig.update_traces(textfont_size=20)  # Adjust the text size
                    st.plotly_chart(fig, use_container_width=True)
        with emr_systems:
            emrs_in_use, emr_implementation, emr_backup, other = st.tabs(
                ['EMRs In Use', 'ERM Implementation', 'EMR Backup', 'Other'])
            with emrs_in_use:
                emsinuse = df_assessment[df_assessment['questionId'].isin([94, 96])]
                sum_df = emsinuse.groupby(['response', 'identifier'])['value'].sum().reset_index()

                # Pivot the data for stacked bar chart
                stacked_df = sum_df.pivot(index='response', columns='identifier', values='value').fillna(0)

                # Calculate percentages
                stacked_df['Percentage'] = (stacked_df['Current Version'] / stacked_df['EMR In Use']) * 100

                # Sort by sum of 'EMR In Use' in descending order
                stacked_df = stacked_df.sort_values(by='EMR In Use', ascending=False)

                # Create stacked bar chart
                fig = go.Figure()

                # Add EMR In Use trace
                fig.add_trace(go.Bar(name='EMR In Use', x=stacked_df.index, y=stacked_df['EMR In Use'],
                                     text=stacked_df['EMR In Use'], textposition='inside'))

                # Add Current Version trace
                fig.add_trace(go.Bar(name='Current Version', x=stacked_df.index, y=stacked_df['Current Version'],
                                     text=stacked_df['Current Version'], textposition='inside'))

                # Add Percentage trace with labels on the nodes
                fig.add_trace(
                    go.Scatter(x=stacked_df.index, y=stacked_df['Percentage'], mode='lines+markers+text', yaxis='y2',
                               name='Percentage', text=(stacked_df['Percentage'].round(2)).astype(str) + '%',
                               textposition='top center', textfont=dict(color='black')))

                # Update layout
                fig.update_layout(
                    title='EMR Systems in Use',
                    xaxis_title='EMR',
                    yaxis_title='Value',
                    yaxis2=dict(
                        title='Percentage',
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    barmode='stack',
                    legend=dict(
                        x=0.5,
                        y=-0.15,
                        orientation='h',
                        traceorder='normal',  # Manually set the legend order
                        itemsizing='constant'  # Prevent legend item resizing
                    )
                )
                # Show the plot
                st.plotly_chart(fig, use_container_width=True)
            with emr_implementation:
                emr_implementations = df_assessment[df_assessment['questionId'].isin([97, 98])]
                sum_df = emr_implementations.groupby(['response', 'question'])['value'].sum().reset_index()

                # Pivot the data for stacked bar chart
                stacked_df = sum_df.pivot(index='response', columns='question', values='value').fillna(0)

                # Calculate total sum of values
                stacked_df['Total'] = stacked_df.sum(axis=1)

                # Sort by total sum of values in descending order
                stacked_df = stacked_df.sort_values(by='Total', ascending=False)

                # Create stacked bar chart
                fig = go.Figure()

                # Add POC trace
                fig.add_trace(go.Bar(name='POC', x=stacked_df.index, y=stacked_df['POC'], text=stacked_df['POC'],
                                     textposition='inside'))

                # Add Retrospective trace
                fig.add_trace(go.Bar(name='Retrospective', x=stacked_df.index, y=stacked_df['Retrospective'],
                                     text=stacked_df['Retrospective'], textposition='inside'))

                # Update layout
                fig.update_layout(
                    title='EMR Implementation',
                    xaxis_title='Program Area',
                    yaxis_title='Number',
                    barmode='stack',
                    legend=dict(
                        x=0.5,
                        y=-0.15,
                        orientation='h',
                        traceorder='normal',  # Manually set the legend order
                        itemsizing='constant'  # Prevent legend item resizing
                    )
                )

                # Show the plot
                st.plotly_chart(fig, use_container_width=True)
            with emr_backup:
                emr_sites = 500
                backup_yes = 300
                backup_no = 200
                backup_yes_central_backup = 100
                backup_yes_external_backup = 200
                backup_yes_external_backup_daily_external = 50
                backup_yes_external_backup_weekly_external = 100
                backup_yes_external_backup_monthly_external = 30
                backup_yes_external_backup_never_external = 20

                # Sankey Diagram
                fig = go.Figure(go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=["EMR Sites", "Backup Yes", "Backup No",
                               "Central Backup", "External Backup",
                               "Daily External", "Weekly External", "Monthly External", "Never External"],
                    ),
                    link=dict(
                        source=[0, 0, 1, 1, 4, 4, 4, 4],
                        target=[1, 2, 3, 4, 5, 6, 7, 8],
                        value=[backup_yes, backup_no,
                               backup_yes_central_backup, backup_yes_external_backup,
                               backup_yes_external_backup_daily_external,
                               backup_yes_external_backup_weekly_external,
                               backup_yes_external_backup_monthly_external,
                               backup_yes_external_backup_never_external],
                    ),
                ))

                st.plotly_chart(fig, use_container_width=True)
            with other:
                mode, sop, rdqa = st.columns([1, 1, 1])
                other_df =  df_assessment[df_assessment['questionId'].isin([100,25,27])]
                with mode:
                    # Group by mode and sum values
                    on_off_grouped_data = other_df[other_df['question'] == 'Data Upload to NDWH'].groupby('response')[
                        'value'].sum().reset_index()
                    on_off_grouped_data['label'] = other_df['question'] + ': ' + on_off_grouped_data['response'].astype(
                        str) + '%'

                    # Plot pie chart
                    fig = px.pie(on_off_grouped_data, values='value', names='response', title='Mode of data upload to NDW',
                                 hole=0.5)
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>: %{percent:%}')
                    fig.update_traces(textfont_size=20)  # Adjust the text size
                    # Update hovertemplate to show custom labels
                    fig.update_traces(hovertemplate='<b>%{label}</b>')

                    # Update layout to position legend at bottom center
                    fig.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig,use_container_width=True)
                with sop:
                    # Group by mode and sum values
                    backup_sops = other_df[other_df['question'] == 'Backup SOPs'].groupby('response')[
                        'value'].sum().reset_index()
                    backup_sops['label'] = other_df['question'] + ': ' + on_off_grouped_data['response'].astype(str) + '%'

                    # Plot pie chart
                    fig = px.pie(backup_sops, values='value', names='response',
                                 title='SOPs to create account backup and access rights', hole=0.5)
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>: %{percent:%}')
                    fig.update_traces(textfont_size=20)  # Adjust the text size
                    # Update hovertemplate to show custom labels
                    fig.update_traces(hovertemplate='<b>%{label}</b>')

                    # Update layout to position legend at bottom center
                    fig.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig,use_container_width=True)
                with rdqa:
                    # Group by mode and sum values
                    backup_sops = df_assessment[df_assessment['question'] == 'EMR Based DQA'].groupby('response')[
                        'value'].sum().reset_index()
                    backup_sops['label'] = df_assessment['question'] + ': ' + on_off_grouped_data['response'].astype(str) + '%'

                    # Plot pie chart
                    fig = px.pie(backup_sops, values='value', names='response', title='EMR Based RDQAs in the last 3 months',
                                 hole=0.5)
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>: %{percent:%}')
                    fig.update_traces(textfont_size=20)  # Adjust the text size
                    # Update hovertemplate to show custom labels
                    fig.update_traces(hovertemplate='<b>%{label}</b>')

                    # Update layout to position legend at bottom center
                    fig.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig,use_container_width=True)

        st.markdown(
            """
            <style>
               #national-performance,#county-performance,#facility-performance{
               font-size: 15px;
               background:#FEFCDD;
               border:1px solid black;
               text-align:center;
               }
               .plot-container{
               
               }
            </style>
            """,
            unsafe_allow_html=True
        )

if selected == 'Data Verification':
    st.header('Data Verification')
    hts, pmtct, prevention, care_and_treatment, kp_program, prep = st.tabs(
        ["HTS", "PMTCT", 'PREVENTION', 'CARE & TREATMENT', 'KP PROGRAM', 'PrEP'])

if selected == 'Data Completeness':
    st.header('Data Completeness')

if selected == 'Service QA':
    st.header('Service Quality Assessment')

footer = """<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://healthstrat.co.ke" target="_blank">Health Strat Limited</a></p>
</div>
"""
# st.markdown(footer, unsafe_allow_html=True)
