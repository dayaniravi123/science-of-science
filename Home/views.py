from django.shortcuts import render
from django.http import HttpResponse

from selenium import webdriver
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import os
import requests
from scholarly import scholarly
import gender_guesser.detector as gender
from scholarly import scholarly
from collections import Counter

## Global variable
authors = []

# Create your views here.
def index(request):
    return render(request, 'Home/home.html')
    #return HttpResponse('Hi, Ravi')

def submit(request):
    conf_name = request.GET.get('conf_name')
    year_name = request.GET.get('year')
    file_name = str(conf_name) + "_" + str(year_name)
    saved_file_name = 'Home/datasets/' + file_name + '.csv'
    request.session['file_name'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        context = data_frame.to_dict('records')

        return render(request, "Home/second.html", {'records': context})

    driver = webdriver.Chrome()
    query = "https://dblp.uni-trier.de/search?q=" + str(conf_name)
    #driver.get("https://dblp.uni-trier.de/search?q=asp-dac")
    driver.get(query)
    divs = driver.find_elements_by_class_name('result-list')

    result = []
    for i in divs[0].find_elements_by_tag_name('a'):
        result.append(i.get_attribute('href'))

    driver.get(result[0])
    all_header = []
    year = []
    Sources = []
    title = driver.find_element_by_class_name('title')
    title = title.text
    place = title.split(",")[-3]
    header = driver.find_elements_by_class_name('publ-list')
    #print(str(year_name))
    for i in header:
        #print(type(i.find_elements_by_tag_name('span')[4].text))
        if i.find_elements_by_tag_name('span')[4].text == str(year_name):
            year.append(i.find_elements_by_tag_name('span')[4].text)
            Sources.append(i.find_elements_by_tag_name('span')[3].text)
            element = i.find_element_by_class_name('toc-link')
            all_header.append(element.get_attribute('href'))
            #print('hi')
        #print(element.get_attribute('href'))
    author_name = []
    paper_name = []
    years = []
    sources = []

    for i in range(len(all_header)):
        driver.get(all_header[i])
        header = driver.find_elements_by_class_name('inproceedings')
        for j in range(len(header)):
            paper_name.append(header[j].find_element_by_class_name('title').text)
            years.append(year[i])
            sources.append(Sources[i])
            temp = []
            for k in header[j].find_elements_by_tag_name('a'):
                if k.text:
                    temp.append(k.text)
                    authors.append(k.text)
            temp = ', '.join(temp)
            author_name.append(temp)

    data_frame = pd.DataFrame({
        #'Authors': author_name,
        'PaperName': paper_name,
        'Year': years,  # [year[0]]*len(author_name),
        'sources': sources,
        'place': [place]*len(sources),
        'authors': author_name
    })

    data_frame_authors = pd.DataFrame({
        'Authors':authors
    })
    saved_file_author_name = 'Home/datasets/author' + file_name + '.csv'
    data_frame_authors.to_csv(saved_file_author_name)
    request.session['file_name_author'] = saved_file_author_name


    data_frame.to_csv(saved_file_name)
    request.session['file_name'] = saved_file_name
    #data_frame.to_csv('Home/datasets/dataset.csv')
    context = data_frame.to_dict('records')

    return render(request, "Home/second.html", {'records':context})


def author(request):
    return render(request, "Home/author.html")

def getauthordetails(request):
    authorName = request.GET.get('author_name')
    search_query = scholarly.search_author(authorName)
    data = next(search_query)
    return render(request, "Home/author.html", data)

def downloadfile(request):
    #path = "Home/datasets/dataset.csv"
    path = request.session['file_name']
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="text/csv")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
        return response
    #return response

def statistics(request):
    detector = gender.Detector()
    gender_data = []
    data = pd.read_csv(str(request.session['file_name_author']))
    authors = list(data['Authors'])
    url = 'https://api.genderize.io?name='
    categories = {'male':0,
                  'female':0,
                  'other':0}
    affiliation = []
    '''
    for i in range(len(authors)):
        edited = url + authors[i].split(" ")[0]
        gender_d = requests.get(edited)
        data = gender_d.json()
        if data['gender']:
            categories[str(data['gender'])] += 1
        else:
            categories['other'] += 1
        

    context = {'keys' : list(categories.keys()),
               'values' : list(categories.values())}
    '''
    ## Statistics about the author data
    '''
    data = pd.read_csv(str(request.session['file_name']))
    authors = list(data['authors'])
    new_author_list = []
    for i in range(len(authors)):
        for j in authors[i].split(", "):
            new_author_list.append(j)
    count_author = Counter(new_author_list)
    df = pd.DataFrame.from_dict(count_author, orient='index', columns=['values'])
    df = df.reset_index()
    df = df.sort_values(by='values', ascending=False)
    top_five_rows = df.iloc[:5,:]
    df = df.sort_values(by='values', ascending=True)
    last_five_rows = df.iloc[:5, :]

    top_rows = top_five_rows.to_dict('records')
    last_rows = last_five_rows.to_dict('records')

    ## Getting Citation count of author
    author_citation = []
    for i in range(len(new_author_list)):
        string_url = new_author_list[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/authors?search=' + string_url
        data = requests.get(url)

        try:
            data = data.json()
            author_citation.append(data['results'][0]['cited_by_count'])
        except:
            author_citation.append(0)
    new_df_author_citation = pd.DataFrame({
        'authorName':new_author_list,
        'authorCitation':author_citation
    })
    new_df_author_citation = new_df_author_citation.sort_values(by='authorCitation', ascending=False)
    top_five_rows_author_citation = new_df_author_citation.iloc[:5, :]

    new_df_author_citation = new_df_author_citation.sort_values(by='authorCitation', ascending=True)
    last_five_rows_author_citation = new_df_author_citation.iloc[:5, :]

    top_five_citations = top_five_rows_author_citation.to_dict('records')
    last_five_citations = last_five_rows_author_citation.to_dict('records')

    return render(request, "Home/piechart.html",
                  {'toprows':top_rows,
                   'lastrows':last_rows,
                   'topcitation':top_five_citations,
                   'lastcitation':last_five_citations})
    '''
    return render(request, "Home/piechart.html")

def statisticsTopCitation(request):
    data = pd.read_csv(str(request.session['file_name']))
    file_name = str(request.session['file_name'])[:-4] + 'statisticsTopCitation'
    saved_file_name = file_name + '.csv'
    request.session['file_name_TCstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        top_five_citations = data_frame.to_dict('records')
        return render(request, "Home/statisticsTopCitation.html",
                      {
                          'topcitation': top_five_citations
                      })

    authors = list(data['authors'])
    new_author_list = []
    for i in range(len(authors)):
        for j in authors[i].split(", "):
            new_author_list.append(j)

    ## Getting Citation count of author
    author_citation = []
    for i in range(len(new_author_list)):
        string_url = new_author_list[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/authors?search=' + string_url
        data = requests.get(url)

        try:
            data = data.json()
            author_citation.append(data['results'][0]['cited_by_count'])
        except:
            author_citation.append(0)
    new_df_author_citation = pd.DataFrame({
        'authorName': new_author_list,
        'authorCitation': author_citation
    })
    new_df_author_citation = new_df_author_citation.sort_values(by='authorCitation', ascending=False)
    top_five_rows_author_citation = new_df_author_citation.iloc[:5, :]
    top_five_rows_author_citation.to_csv(saved_file_name)
    request.session['file_name_TCstatistics'] = saved_file_name

    top_five_citations = top_five_rows_author_citation.to_dict('records')

    return render(request, "Home/statisticsTopCitation.html",
                  {
                   'topcitation': top_five_citations
                    })

def statisticsLastCitation(request):
    data = pd.read_csv(str(request.session['file_name']))
    file_name = str(request.session['file_name'])[:-4] + 'statisticsLastCitation'
    saved_file_name = file_name + '.csv'
    request.session['file_name_LCstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        last_five_citations = data_frame.to_dict('records')
        return render(request, "Home/statisticsLastCitation.html",
                      {
                          'lastcitation': last_five_citations})

    authors = list(data['authors'])
    new_author_list = []
    for i in range(len(authors)):
        for j in authors[i].split(", "):
            new_author_list.append(j)

    ## Getting Citation count of author
    author_citation = []
    for i in range(len(new_author_list)):
        string_url = new_author_list[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/authors?search=' + string_url
        data = requests.get(url)

        try:
            data = data.json()
            author_citation.append(data['results'][0]['cited_by_count'])
        except:
            author_citation.append(0)
    new_df_author_citation = pd.DataFrame({
        'authorName': new_author_list,
        'authorCitation': author_citation
    })

    new_df_author_citation = new_df_author_citation.sort_values(by='authorCitation', ascending=True)
    last_five_rows_author_citation = new_df_author_citation.iloc[:5, :]
    last_five_rows_author_citation.to_csv(saved_file_name)
    request.session['file_name_LCstatistics'] = saved_file_name

    last_five_citations = last_five_rows_author_citation.to_dict('records')

    return render(request, "Home/statisticsLastCitation.html",
                  {
                   'lastcitation': last_five_citations})


def statisticsMostCommonAuthor(request):
    data = pd.read_csv(str(request.session['file_name']))

    file_name = str(request.session['file_name'])[:-4] + 'statisticsMostCommonAuthor'
    saved_file_name = file_name + '.csv'
    request.session['file_name_MCAstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        top_rows = data_frame.to_dict('records')

        return render(request, "Home/statisticsMostCommonAuthor.html",
                      {'toprows': top_rows
                       })

    authors = list(data['authors'])
    new_author_list = []
    for i in range(len(authors)):
        for j in authors[i].split(", "):
            new_author_list.append(j)
    count_author = Counter(new_author_list)
    df = pd.DataFrame.from_dict(count_author, orient='index', columns=['values'])
    df = df.reset_index()
    df = df.sort_values(by='values', ascending=False)
    top_five_rows = df.iloc[:5, :]
    top_five_rows.to_csv(saved_file_name)
    request.session['file_name_MCAstatistics'] = saved_file_name

    top_rows = top_five_rows.to_dict('records')

    return render(request, "Home/statisticsMostCommonAuthor.html",
                  {'toprows': top_rows
                    })

def statisticsLeastCommonAuthor(request):
    data = pd.read_csv(str(request.session['file_name']))
    file_name = str(request.session['file_name'])[:-4] + 'statisticsLeastCommonAuthor'
    saved_file_name = file_name + '.csv'
    request.session['file_name_LCAstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        last_rows = data_frame.to_dict('records')
        return render(request, "Home/statisticsLeastCommonAuthor.html",
                      {
                          'lastrows': last_rows
                      })

    authors = list(data['authors'])
    new_author_list = []
    for i in range(len(authors)):
        for j in authors[i].split(", "):
            new_author_list.append(j)
    count_author = Counter(new_author_list)
    df = pd.DataFrame.from_dict(count_author, orient='index', columns=['values'])
    df = df.reset_index()
    df = df.sort_values(by='values', ascending=True)
    last_five_rows = df.iloc[:5, :]
    last_five_rows.to_csv(saved_file_name)
    request.session['file_name_LCAstatistics'] = saved_file_name
    last_rows = last_five_rows.to_dict('records')
    return render(request, "Home/statisticsLeastCommonAuthor.html",
                  {
                   'lastrows': last_rows
                    })


def statisticsPaperTopRows(request):
    dataset = pd.read_csv(str(request.session['file_name']))

    file_name = str(request.session['file_name'])[:-4] + 'statisticsPaperTopRows'
    saved_file_name = file_name + '.csv'
    request.session['file_name_PTRstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        top_five_citations = data_frame.to_dict('records')
        return render(request, "Home/statisticsPaperTopRows.html",
                      {
                          'toppaper': top_five_citations
                      })

    papers = list(dataset['PaperName'])
    citations_per_paper = []

    for i in range(len(papers)):
        string_url = papers[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?search=' + string_url

        data = requests.get(url)
        data = data.json()
        try:
            d = data['results'][0]
            citations_per_paper.append(d['cited_by_count'])
        except:
            citations_per_paper.append(0)

    new_df_paper_citation = pd.DataFrame({
        'paperName': papers,
        'paperCitation': citations_per_paper
    })
    new_df_paper_citation = new_df_paper_citation.sort_values(by='paperCitation', ascending=False)
    top_five_rows_paper_citation = new_df_paper_citation.iloc[:5, :]
    top_five_rows_paper_citation.to_csv(saved_file_name)
    request.session['file_name_PTRstatistics'] = saved_file_name
    top_five_citations = top_five_rows_paper_citation.to_dict('records')

    return render(request, "Home/statisticsPaperTopRows.html",
                  {
                      'toppaper': top_five_citations
                  })

def statisticsPaperLastRows(request):
    dataset = pd.read_csv(str(request.session['file_name']))
    file_name = str(request.session['file_name'])[:-4] + 'statisticsPaperLastRows'
    saved_file_name = file_name + '.csv'
    request.session['file_name_PLRstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        last_five_citations = data_frame.to_dict('records')
        return render(request, "Home/statisticsPaperLastRows.html",
                    {
                          'lastpaper': last_five_citations
                      })

    papers = list(dataset['PaperName'])
    citations_per_paper = []

    for i in range(len(papers)):
        string_url = papers[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?search=' + string_url

        data = requests.get(url)
        data = data.json()
        try:
            d = data['results'][0]
            citations_per_paper.append(d['cited_by_count'])
        except:
            citations_per_paper.append(0)

    new_df_paper_citation = pd.DataFrame({
        'paperName': papers,
        'paperCitation': citations_per_paper
    })

    new_df_paper_citation = new_df_paper_citation.sort_values(by='paperCitation', ascending=True)
    last_five_rows_paper_citation = new_df_paper_citation.iloc[:5, :]
    last_five_rows_paper_citation.to_csv(saved_file_name)
    request.session['file_name_PLRstatistics'] = saved_file_name
    last_five_citations = last_five_rows_paper_citation.to_dict('records')

    return render(request, "Home/statisticsPaperLastRows.html",
                  {
                      'lastpaper':last_five_citations
                  })


def authorStatistics(request):
    data = pd.read_csv(str(request.session['file_name']))

    file_name = str(request.session['file_name'])[:-4] + 'authorStatistics'
    saved_file_name = file_name + '.csv'
    request.session['file_name_authorstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        data = data_frame.to_dict('records')
        return render(request, "Home/authorStatistics.html",{'context':data})

    papernames = list(data['PaperName'])
    author_name = []
    author_affiliation = []
    author_country = []
    for i in range(len(papernames)):
        string_url = papernames[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?search=' + string_url
        data = requests.get(url)

        try:
            data = data.json()
            all_authors = data['results'][0]['authorships']
            for j in range(len(all_authors)):
                author_name.append(all_authors[j]['author']['display_name'])
                temp = all_authors[j]['raw_affiliation_string'].split(",")
                author_affiliation.append(temp[0])
                author_country.append(temp[-1])
        except:
            continue
    res = Counter(author_affiliation)
    data_frame = pd.DataFrame.from_dict(res, orient="index", columns=["values"])
    data_frame = data_frame.reset_index()
    data_frame.to_csv(saved_file_name)
    request.session['file_name_authorstatistics'] = saved_file_name

    data = data_frame.to_dict('records')

    return render(request, "Home/authorStatistics.html",{'context':data})