from config import MAIN_PAGE

import streamlit as st


def main():
    main_page = st.Page(MAIN_PAGE, title="Main Page")

    pages = st.navigation([main_page])

    pages.run()


if __name__ == "__main__":
    main()