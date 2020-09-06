# Cardamom Scraper

Tool for collecting minority language data from social media

## Quick start for setting up Airflow

Make sure:

    1- port 8080 is available 

    2- you have python3 as 'terminal command' 
        otherwise change in run.sh python3 to your python in line 2 
    3- your run.sh that is inside the my_cardamon/ folder has the right permissions to run 
       chmod +x ./run.sh might be useful 
    4- your terminal session has the rights to create folder and others 
       ```sudo -s``` ** or similar to guarantee you have root rights
            
then run those commands in your terminal:

```git clone https://gitlab.insight-centre.org/uld/cardamom-scraper.git my_cardamom_folder```

```cd ./my_cardamom_folder```


```source run.sh```

after running this you terminal should print a log similar to this:

![terminal](terminal.png)

You then can access http://localhost:8080 , you should see:

![airflow](airflow.png)
