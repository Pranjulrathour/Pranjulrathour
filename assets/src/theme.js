// render.py loads each panel twice: hero.html (dark) and hero.html?light (light). The class drives art.css tokens.
if (location.search.includes("light")) document.documentElement.classList.add("light");
