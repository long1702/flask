import unittest
import mongomock
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from pandas import testing as pd_testing
from user_interface import form_layout, form_pipe_line, form_dataframe
from mock import patch, Mock
from datetime import datetime

DATE_GROUP = {
    "month": { "$month": "$created_date" },
    "year": { "$year": "$created_date" },
    "date": {"$dayOfMonth": "$created_date"},
    "model": "$predict.model"
}
MONTH_GROUP = {
    "month": { "$month": "$created_date" },
    "year": { "$year": "$created_date" },
    "model": "$predict.model"
}
YEAR_GROUP = {
    "year": { "$year": "$created_date" },
    "model": "$predict.model"
}
START_DATE = datetime(2020, 9, 2)
END_DATE = datetime(2020, 9, 4)
 

class Test_UI_function(unittest.TestCase):
    def setUp(self):
        self.mock_get_database_patcher = patch('user_interface.DB', mongomock.MongoClient().database)
        self.mock_get_database = self.mock_get_database_patcher.start()
        
    def tearDown(self):
        self.mock_get_database_patcher.stop()
        
    def form_pipe_line_with_keys_group(self, keys, group):
        pipe_line = [{
                "$match": keys,
            },
            {
                "$unwind": "$predict"
            },
            {
                "$group": {
                    "_id": group,
                    "true_positive": {
                        "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", True]}, {"$eq":["$predict.label", True]}]}, 1, 0 ]}
                    },
                    "false_positive": {
                        "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", True]}, {"$eq":["$predict.label", False]}]}, 1, 0 ]}
                    },
                    "false_negative": {
                        "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", False]}, {"$eq":["$predict.label", True]}]}, 1, 0 ]}
                    },
                    "created_date": {"$min": "$created_date"}
            }
        }]
        return pipe_line

    def form_dataframe_basic(self, grouped_by_type, data):
        if grouped_by_type == 'MONTH':
            prensent_func = lambda x: datetime(year=x.year,month=x.month,day=1)
        elif grouped_by_type == 'YEAR':
            prensent_func = lambda x: datetime(year=x.year,month=1,day=1)
        else:
            prensent_func = lambda x: datetime(x.year,x.month,x.day)

        df = pd.DataFrame(data=data)
        if df.empty:
            return df
        df["model"] = list(map(lambda x: x.get("model", "None"), df["_id"]))
        df["precision"] = df["true_positive"] / (df["true_positive"] + df["false_positive"])
        df["recall"] = df["true_positive"] / (df["true_positive"] + df["false_negative"])
        df["created_date"] = list(map(prensent_func, df['created_date']))
        df = df[["precision", "recall", "created_date", "model"]]
        df=df.sort_values(by=["created_date"])
        return df

    @patch('user_interface.DB.mention')
    def test_all_topic_called_with(self, mock_DB_mention):
        mock_DB_mention.aggregate = Mock(return_value=[])
        keys = {"created_date": {"$gt": START_DATE, "$lt": END_DATE}}
        keys["is_updated"] = True

        _ = form_layout(START_DATE, END_DATE, "DATE")
        pipe_line = self.form_pipe_line_with_keys_group(keys, DATE_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

        _ = form_layout(START_DATE, END_DATE, "MONTH")
        pipe_line = self.form_pipe_line_with_keys_group(keys, MONTH_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

        _ = form_layout(START_DATE, END_DATE, "YEAR")
        pipe_line = self.form_pipe_line_with_keys_group(keys, YEAR_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

    @patch('user_interface.DB.mention')
    def test_topic_called_with(self, mock_DB_mention):
        mock_DB_mention.aggregate = Mock(return_value=[])
        keys = {"created_date": {"$gt": START_DATE, "$lt": END_DATE}}
        keys["is_updated"] = True
        keys["topic_id"] = 123
        

        _ = form_layout(START_DATE, END_DATE, "DATE", 123)
        pipe_line = self.form_pipe_line_with_keys_group(keys, DATE_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

        _ = form_layout(START_DATE, END_DATE, "MONTH", 123)
        pipe_line = self.form_pipe_line_with_keys_group(keys, MONTH_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

        _ = form_layout(START_DATE, END_DATE, "YEAR", 123)
        pipe_line = self.form_pipe_line_with_keys_group(keys, YEAR_GROUP)
        mock_DB_mention.aggregate.assert_called_with(pipe_line)

    def test_form_pipe_line_topic(self):
        keys = {"created_date": {"$gt": START_DATE, "$lt": END_DATE}}
        keys["topic_id"] = 123
        keys["is_updated"] = True

        pipe_line_1 = form_pipe_line(START_DATE, END_DATE, "DATE", 123)
        return_pipe_line_1 = self.form_pipe_line_with_keys_group(keys, DATE_GROUP)
        self.assertEqual(pipe_line_1, return_pipe_line_1)


        pipe_line_1 = form_pipe_line(START_DATE, END_DATE, "MONTH", 123)
        return_pipe_line_1 = self.form_pipe_line_with_keys_group(keys, MONTH_GROUP)
        self.assertEqual(pipe_line_1, return_pipe_line_1)

        pipe_line_1 = form_pipe_line(START_DATE, END_DATE, "YEAR", 123)
        return_pipe_line_1 = self.form_pipe_line_with_keys_group(keys, YEAR_GROUP)
        self.assertEqual(pipe_line_1, return_pipe_line_1)


    def test_form_pipe_line_all(self):
        keys = {"created_date": {"$gt": START_DATE, "$lt": END_DATE}}
        keys["is_updated"] = True

        pipe_line_2 = form_pipe_line(START_DATE, END_DATE, "DATE", "All Topic")
        return_pipe_line_2 = self.form_pipe_line_with_keys_group(keys, DATE_GROUP)
        self.assertEqual(pipe_line_2, return_pipe_line_2)

        pipe_line_2 = form_pipe_line(START_DATE, END_DATE, "MONTH", "All Topic")
        return_pipe_line_2 = self.form_pipe_line_with_keys_group(keys, MONTH_GROUP)
        self.assertEqual(pipe_line_2, return_pipe_line_2)

        pipe_line_2 = form_pipe_line(START_DATE, END_DATE, "YEAR", "All Topic")
        return_pipe_line_2 = self.form_pipe_line_with_keys_group(keys, YEAR_GROUP)
        self.assertEqual(pipe_line_2, return_pipe_line_2)

    def test_form_dataframe_date(self):
        RETURN_VALUE_DATE =[{
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        }]

        ref_df = self.form_dataframe_basic("DATE", RETURN_VALUE_DATE)
        df = form_dataframe(RETURN_VALUE_DATE, "DATE")
        pd_testing.assert_frame_equal(ref_df, df)

    def test_form_dataframe_month(self):
        RETURN_VALUE_MONTH =[{
            "_id": {
                "year": 2020,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 8, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 10,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 10, 2)
        }]

        ref_df = self.form_dataframe_basic("MONTH", RETURN_VALUE_MONTH)
        df = form_dataframe(RETURN_VALUE_MONTH, "MONTH")

        pd_testing.assert_frame_equal(ref_df, df)

    def test_form_dataframe_year(self):
        RETURN_VALUE_YEAR =[{
            "_id": {
                "year": 2019,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2019, 8, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 8, 2)
        },
        {
            "_id": {
                "year": 2021,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2021, 8, 2)
        }]
        
        ref_df = self.form_dataframe_basic("YEAR", RETURN_VALUE_YEAR)
        df = form_dataframe(RETURN_VALUE_YEAR, "YEAR")
        pd_testing.assert_frame_equal(ref_df, df)

    def test_form_dataframe_model(self):
        RETURN_VALUE_MODEL =[{
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        }]
        ref_df = self.form_dataframe_basic("DATE", RETURN_VALUE_MODEL)
        df = form_dataframe(RETURN_VALUE_MODEL, "DATE")
        pd_testing.assert_frame_equal(ref_df, df)
        
    @patch('user_interface.DB.mention')
    def test_form_layout_empty(self, mock_DB_mention):
        mock_DB_mention.aggregate = Mock(return_value=[])
        empty_layout = form_layout(START_DATE, END_DATE, DATE_GROUP)
        self.assertEqual(empty_layout, [])
        

    @patch('user_interface.DB.mention')
    def test_form_layout_date(self, mock_DB_mention):
        RETURN_VALUE_DATE =[{
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        }]

        mock_DB_mention.aggregate = Mock(return_value=RETURN_VALUE_DATE)
        layout = form_layout(START_DATE, END_DATE, "DATE")

        df = form_dataframe(RETURN_VALUE_DATE, "DATE")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["precision"],
                            mode='lines',
                            name='precision'))
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["recall"],
                            mode='lines',
                            name='recall'))

        fig.update_layout(
            font_color='#000000',
            title="Precision and Recall of Model v1",
            xaxis_title="Timeline",
            yaxis=dict(range=[0,1])
        )

        ref_layout = [
            dcc.Graph(
                id='graph_of_model_v1',
                figure=fig
        )]
        
        self.assertEqual(str(layout), str(ref_layout))

    @patch('user_interface.DB.mention')
    def test_form_layout_month(self, mock_DB_mention):
        RETURN_VALUE_MONTH =[{
            "_id": {
                "year": 2020,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 8, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 10,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 10, 2)
        }]
        mock_DB_mention.aggregate = Mock(return_value=RETURN_VALUE_MONTH)
        layout = form_layout(START_DATE, END_DATE, "MONTH")

        df = form_dataframe(RETURN_VALUE_MONTH, "MONTH")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["precision"],
                            mode='lines',
                            name='precision'))
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["recall"],
                            mode='lines',
                            name='recall'))

        fig.update_layout(
            font_color='#000000',
            title="Precision and Recall of Model v1",
            xaxis_title="Timeline",
            yaxis=dict(range=[0,1])
        )

        ref_layout = [
            dcc.Graph(
                id='graph_of_model_v1',
                figure=fig
        )]
        
        self.assertEqual(str(layout), str(ref_layout))

    @patch('user_interface.DB.mention')
    def test_form_layout_year(self, mock_DB_mention):
        RETURN_VALUE_YEAR =[{
            "_id": {
                "year": 2019,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2019, 8, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 8, 2)
        },
        {
            "_id": {
                "year": 2021,
                "month": 8,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2021, 8, 2)
        }]
        mock_DB_mention.aggregate = Mock(return_value=RETURN_VALUE_YEAR)
        layout = form_layout(START_DATE, END_DATE, "YEAR")

        df = form_dataframe(RETURN_VALUE_YEAR, "YEAR")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["precision"],
                            mode='lines',
                            name='precision'))
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["recall"],
                            mode='lines',
                            name='recall'))

        fig.update_layout(
            font_color='#000000',
            title="Precision and Recall of Model v1",
            xaxis_title="Timeline",
            yaxis=dict(range=[0,1])
        )

        ref_layout = [
            dcc.Graph(
                id='graph_of_model_v1',
                figure=fig
        )]
        
        self.assertEqual(str(layout), str(ref_layout))

    @patch('user_interface.DB.mention')
    def test_form_layout_model(self, mock_DB_mention):
        RETURN_VALUE_MODEL =[{
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 2,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 2)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 3,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 3)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v1"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        },
        {
            "_id": {
                "year": 2020,
                "month": 9,
                "date": 4,
                "model": "v2"
            },
            "true_positive": 10,
            "false_positive": 20,
            "false_negative": 5,
            "created_date": datetime(2020, 9, 4)
        }]
        mock_DB_mention.aggregate = Mock(return_value=RETURN_VALUE_MODEL)
        layout = form_layout(START_DATE, END_DATE, "DATE")

        df = form_dataframe(RETURN_VALUE_MODEL, "DATE")
        grouped_df = df.groupby(df["model"])
        ref_layout = []
        for name, df in grouped_df:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["created_date"], y=df["precision"],
                                mode='lines',
                                name='precision'))
            fig.add_trace(go.Scatter(x=df["created_date"], y=df["recall"],
                                mode='lines',
                                name='recall'))

            fig.update_layout(
                font_color='#000000',
                title="Precision and Recall of Model {}".format(name),
                xaxis_title="Timeline",
                yaxis=dict(range=[0,1])
            )

            ref_layout.append(
                dcc.Graph(
                    id='graph_of_model_{}'.format(name),
                    figure=fig
                )
            )
                
        self.assertEqual(str(layout), str(ref_layout))
