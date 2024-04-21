
![TMDB Movie Data Analysis](https://raw.githubusercontent.com/dkalenov/TMDB-Movie-Data-Analysis/main/assets/TMDB-image.png)

## Project objectives

Conduct data analysis; load data into the database; test hypotheses.

### Hypothesis 1: the more films are released per year, the more “dollar billionaires” there are among them.

Tasks:
- Sort films that have grossed more than a billion US dollars by year of release, count their number per year;
Determine the total number of films released in those years when at least one billion-dollar film was released;
Establish the dependence of the number of “billionaire films” on the total number of films released.

### Hypothesis 2: Action films make the biggest profits in absolute and relative terms.

Tasks:
- Sort films by genre and calculate average profit;
Find total profit and by genre;
Determine what place in the ranking of overall genre profits are films of the “action” genre;
Calculate the total number of films released by genre and calculate the profit percentage;

### Hypothesis 3: Remakes of films that have the same name as the original bring more profit than the original itself.

Tasks:
- Sort films that have the same title but different release dates;
Compare the average box office receipts of similar films in absolute and relative terms.

## Conclusion
- The number of films released per year is not a factor in the increase in the number of films grossing more than a billion US dollars. On the contrary, statistics for 2013, 2014, 2021, and 2022 show an inverse relationship.

  ![The number of movies by years](https://github.com/dkalenov/TMDB-Movie-Data-Analysis/blob/main/assets/number%20of%20movies.jpg)

- In terms of average profit, action films rank 6th, with an average profit of $120,617,200. In terms of profit percentage, action films average a profit margin of 407%, ranking 16th out of the 19 genres examined. In terms of overall box office receipts, films in the “action” genre are also not leaders and are in second place, behind films in the “adventure” genre in terms of overall box office receipts.
  ![Top box office](https://github.com/dkalenov/TMDB-Movie-Data-Analysis/blob/main/assets/top%20box%20office.jpg)

- Remakes of films that have the same name as the originals bring in more than 2 times the profit compared to the originals. However, in percentage terms, the profit of remakes is significantly inferior to the originals, so for greater objectivity in the future it is worth considering the profit of the originals and remakes taking into account inflation.
  ![Top box office](https://github.com/dkalenov/TMDB-Movie-Data-Analysis/blob/main/assets/original%20%26%20remakes.jpg)

## Further development

Train a neural network to recommend movies based on user preferences

## Skills and tools 

* Data analysis
* Python
* Pandas
* Matplotlib
* SQL
* SQLite

## Project status
- [x] Data analysis
- [x] Load data into the database
- [x] Test hypotheses
- [ ] Train a neural network to recommend movies based on user preferences
