[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/ian-shepherd/soccer/main/soccer_dashboard.py)

# Soccer Dashboard
This app runs on streamlit and is meant to provide a summary of player performance for all players who played in any of the Big 5 leagues (Bundelisga, EPL, La Liga, Ligue 1, Serie A) from 2017-2018 season to present or Europa/Champions League 2018-2019 season to present. However, the dashboard itself is merely a piece of the entire process. Included in this repositories is my entire process for scraping data from websites, clean the data, and then build/manage a database that ultimately powers the app. Inspiration for this dashboard came from Max Bolger's NFL Receiver Dashboard (https://github.com/maxbolger/nfl-receiver-dashboard). I also want to give a special thanks to FC Python as well as their tutorials helped me out a lot in my early stages of using python for soccer data.


## Data Sources
All data comes from fbref, including their StatsBomb data, and Transfermarkt. I cannot stress enough that when scraping websites, please do it respectfully. I always include sleep stoppages in my scripts between calls so my scripts can at least somewhat resemble human browsing.

[<img align="middle" alt="Python" width="75px" src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcode.fb.com%2Fwp-content%2Fuploads%2F2016%2F05%2F2000px-Python-logo-notext.svg_.png&f=1&nofb=1" />][Python]
[<img align="middle" alt="streamlit" width="150px" src="https://assets.website-files.com/5dc3b47ddc6c0c2a1af74ad0/5e181828ba9f9e92b6ebc6e7_RGB_Logomark_Color_Light_Bg.png" />][streamlit]
[<img align="middle" alt="fbref" width="150px" src="https://d2p3bygnnzw9w3.cloudfront.net/req/202101292/logos/fb-logo.svg" />][fbref]
[<img align="middle" alt="Transfermarkt" width="150px" src="https://tmsi.akamaized.net/head/transfermarkt_logo.svg" />][Transfermarkt]
[<img align="middle" alt="fcpython" width="75px" src="https://fcpython.com/wp-content/uploads/2017/12/Logocomp9.png" />][fcpython]

[Python]: https://www.python.org/
[streamlit]: https://www.streamlit.io/
[fbref]: https://fbref.com/
[Transfermarkt]: https://transfermarkt.com/
[fcpython]: https://fcpython.com/

# Roadmap
- Mobile friendly
- Some sort of identifier to show where players rank for p90 stats
- Player comparison tool
- Time comparison (i.e. compare a player's current season to previous)


## Disclaimers
I have a very specific folder structure stored locally that works for me and it isn't exactly the same as laid out on GitHub. Consequently, the folder path variables would have to be tweaked in each of the scripts unless you have the same folder structure as me.