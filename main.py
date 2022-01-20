import os
from typing import Optional, List
from fastapi import FastAPI, Request, File, UploadFile, Form
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from process_ import ForecastingProcess, plotly_df

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="random secret key")   # add middleware for use request.session
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")

'''
freq_ = {
    "B" : "business day frequency",
    "D" : "calendar day frequency",
    "W-SUN" : "weekly frequency (Sundays)",
    "W-MON" : "weekly frequency (Mondays)",
    "W-TUE" : "weekly frequency (Tuesdays)",
    "W-WED" : "weekly frequency (Wednesdays)",
    "W-THU" : "weekly frequency (Thursdays)",
    "W-FRI" : "weekly frequency (Fridays)",
    "W-SAT" : "weekly frequency (Saturdays)",
    "M" : "month end frequency",
    "SM" : "semi-month end frequency (15th and end of month)",
    "BM" : "business month end frequency",
    "MS" : "month start frequency",
    "SMS" : "semi-month start frequency (1st and 15th)"
}
'''
forecastingModel = {1: "Prophet"}           # append other model and add the similar forecast function in ProcessFuntion in process_.py
forecastingProcess = ForecastingProcess()
session = {}
def init_session():
    session = {"original_data": "",
                "demo_data": "",
                "time_series_data": "",
                "field_": "",
                "metric": {},
                "dimension": "",
                "column_header": [],
                "plot_df": "",
                "plot_component_df": "",
                "warning0": "",
                "warning1": "",
                "freq_df_": "",
                "model_": "",
                "prediction_size_": "",
                "adf": "",
                "err": "",
                "numDiff": "",
                "smode_" : ""
                }
    return session
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        print(request.session["access"])
    except:
        request.session["access"] = os.urandom(12).hex()
        session[request.session["access"]] = init_session()
    id = request.session["access"]
    if id not in session:                               
        session[id] = init_session()
    return template.TemplateResponse("index.html", {"request": request, 
                                                    "warning0": session[id]["warning0"] if id in session else "",
                                                    "warning1": session[id]["warning1"] if id in session else "",
                                                    "demo_data": session[id]["demo_data"] if id in session else "",
                                                    "visualize_forecast": session[id]["plot_df"] if id in session else "",
                                                    "visualize_forecast_component": session[id]["plot_component_df"] if id in session else "",
                                                    "field_data": session[id]["metric"] if id in session else "",
                                                    "field_choosed": session[id]["field_"] if id in session else "",
                                                    "seasonality_mode": session[id]["smode_"] if id in session else "",
                                                    "frequence": session[id]["freq_df_"] if id in session else "",
                                                    "prediction_size": session[id]["prediction_size_"] if id in session else "",
                                                    "models": forecastingModel,
                                                    "model_choosed": session[id]["model_"] if id in session else "",
                                                    "note_adf": session[id]['adf'] if id in session else "",
                                                    "note_err": session[id]['err'] if id in session else "",
                                                    "note_numDiff": session[id]['numDiff'] if id in session else ""})

@app.post("/uploadfiles/")
async def create_upload_files(request: Request, files: List[UploadFile] = File(...)):
    '''
        upload csv file and handle, visualize the history data
    '''
    id = request.session["access"]
    print(len(files))
    if len(files) > 1:                                          # upload more than one file
        session[id]["warning0"] = "Only upload 1 file"
        return RedirectResponse("/", 303)
    elif len(files) == 0:                                       # nothing file have been uploaded
        session[id]["warning0"] = "Nothing have been uploaded"
        return RedirectResponse("/", 303)
    elif len(files) == 1:  
        f = files[0]
        if f.filename.endswith('.csv'):                         # correct data: process
            session[id]["warning0"] =  "Done: " + f.filename  
            try:
                
                session[id]["original_data"] = pd.read_csv(f.file)
                od = session[id]["original_data"]

                session[id]["column_header"] = []
                for i in od.columns:
                    session[id]["column_header"].append(i)

                session[id]["dimension"] = session[id]["column_header"][0]
                tmp = session[id]["column_header"][1]           # check exist > 1 columns, if is not, raise error
                session[id]["metric"] = {}
                for i in range(1,len(session[id]["column_header"])): 
                    session[id]["metric"][ session[id]["column_header"][i] ] = i      
            except:
                session[id]["warning0"] = "! Unsuccessful, file upload is incorrect (unreadable)"
                return RedirectResponse("/", 303) 

            session[id]["time_series_data"] = ""
            session[id]["field_"] = ""
            session[id]["demo_data"] = plotly_df(od, session[id]["column_header"][0], "Demo history data")

            return RedirectResponse("/", 303)
        else:                                                   # incorrect data
            session[id]["warning0"] = "! Unsuccessful, file upload is not csv file"
            return RedirectResponse("/", 303)

@app.post("/cfd/")
def get_field(request: Request, field: str = Form(...), smode: str = Form(...)):
    '''
        Get the column for forecast and prepare the correct dataframe
    '''
    id = request.session["access"]

    session[id]["field_"] = field
    session[id]["smode_"] = smode
    original_data = session[id]["original_data"]
    dimension = session[id]["dimension"]
    time_series_data = original_data[[dimension,field]].copy()
    time_series_data.rename(index=str, columns={dimension: "ds", field: "y"}, inplace=True) 

    session[id]["time_series_data"] = time_series_data
    session[id]["plot_component_df"] = ""
    session[id]["plot_df"] = ""
    session[id]["freq_df_"] = ""
    session[id]["prediction_size_"] = ""
    print(field)
    print(time_series_data)
    return RedirectResponse("/", 303)

@app.post("/uploadoption/")
def get_option(request: Request, freq_: str = Form(...), prediction_size: int = Form(...)):
    '''
        get frequence of dataframe and call the forecast function (solve_)
    '''
    id = request.session["access"]

    session[id]["freq_df_"] = freq_
    session[id]["prediction_size_"] = prediction_size

    session[id]["plot_component_df"] = ""
    session[id]["plot_df"] = ""
    print(freq_)
    print(prediction_size)
    return RedirectResponse("/", 303)
    
@app.post("/getmodel/")
def get_model(request: Request, model: str = Form(...)):

    print(model)
    id = request.session["access"]
    try:
        session[id]["model_"] = model
        time_series_data = session[id]["time_series_data"]
        model_ = session[id]["model_"]
        prediction_size = session[id]["prediction_size_"]
        freq_df_ = session[id]["freq_df_"]
        field_ = session[id]["field_"]
        smode = session[id]['smode_']
        fig = forecastingProcess.processFunction[model_](time_series_data, 
                                                        prediction_size, 
                                                        freq_df_, field_, 
                                                        smode)

        session[id]["plot_df"] = fig[0]
        session[id]["plot_component_df"] = fig[1]
        session[id]['adf'] = fig[2]
        session[id]['err'] = fig[3]
        session[id]['numDiff'] = fig[4]
        return RedirectResponse("/", 303)
    except:
        session[id]["warning1"] = "! Incorrect data, can't forecast"
        return RedirectResponse("/", 303)
