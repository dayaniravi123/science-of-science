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
from serpapi import GoogleSearch
from selenium.webdriver.common.by import By

## Global variable
authors = []

import math
import urllib
import urllib.request as urllib2
import xml.etree.ElementTree as ET
import json
import ast


# from scholarly import scholarly


class XPLORE:
    # API endpoint (all non-Open Access)
    endPoint = "http://ieeexploreapi.ieee.org/api/v1/search/articles"

    # Open Access Document endpoint
    openAccessEndPoint = "http://ieeexploreapi.ieee.org/api/v1/search/document/"

    def __init__(self, apiKey):

        # API key
        self.apiKey = apiKey

        # flag that some search criteria has been provided
        self.queryProvided = False

        # flag for Open Access, which changes endpoint in use and limits results to just Open Access
        self.usingOpenAccess = False

        # flag that article number has been provided, which overrides all other search criteria
        self.usingArticleNumber = False

        # flag that a boolean method is in use
        self.usingBoolean = False

        # flag that a facet is in use
        self.usingFacet = False

        # flag that a facet has been applied, in the event that multiple facets are passed
        self.facetApplied = False

        # data type for results; default is json (other option is xml)
        self.outputType = 'json'

        # data format for results; default is raw (returned string); other option is object
        self.outputDataFormat = 'raw'

        # default of 25 results returned
        self.resultSetMax = 2000

        # maximum of 200 results returned
        self.resultSetMaxCap = 20000

        # records returned default to position 1 in result set
        self.startRecord = 1

        # default sort order is ascending; could also be 'desc' for descending
        self.sortOrder = 'asc'

        # field name that is being used for sorting
        self.sortField = 'article_title'

        # array of permitted search fields for searchField() method
        self.allowedSearchFields = ['abstract', 'affiliation', 'article_number', 'article_title', 'author',
                                    'boolean_text', 'content_type', 'd-au', 'd-pubtype', 'd-publisher', 'd-year', 'doi',
                                    'end_year', 'facet', 'index_terms', 'isbn', 'issn', 'is_number', 'meta_data',
                                    'open_access', 'publication_number', 'publication_title', 'publication_year',
                                    'publisher', 'querytext', 'start_year', 'thesaurus_terms']

        # dictionary of all search parameters in use and their values
        self.parameters = {}

        # dictionary of all filters in use and their values
        self.filters = {}

    # ensuring == can be used reliably
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    # ensuring != can be used reliably
    def __ne__(self, other):
        return not self.__eq__(other)

    # set the data type for the API output
    # string outputType   Format for the returned result (JSON, XML)
    # return void
    def dataType(self, outputType):

        outputType = outputType.strip().lower()
        self.outputType = outputType

    # set the data format for the API output
    # string outputDataFormat   Data structure for the returned result (raw string or object)
    # return void
    def dataFormat(self, outputDataFormat):

        outputDataFormat = outputDataFormat.strip().lower()
        self.outputDataFormat = outputDataFormat

    # set the start position in the
    # string start   Start position in the returned data
    # return void
    def startingResult(self, start):

        self.startRecord = math.ceil(start) if (start > 0) else 1

    # set the maximum number of results
    # string maximum   Max number of results to return
    # return void
    def maximumResults(self, maximum):

        self.resultSetMax = math.ceil(maximum) if (maximum > 0) else 25
        if self.resultSetMax > self.resultSetMaxCap:
            self.resultSetMax = self.resultSetMaxCap

    # setting a filter on results
    # string filterParam   Field used for filtering
    # string value    Text to filter on
    # return void
    def resultsFilter(self, filterParam, value):

        filterParam = filterParam.strip().lower()
        value = value.strip()

        if len(value) > 0:
            self.filters[filterParam] = value
            self.queryProvided = True

            # Standards do not have article titles, so switch to sorting by article number
            if (filterParam == 'content_type' and value == 'Standards'):
                self.resultsSorting('publication_year', 'asc')

    # setting sort order for results
    # string field   Data field used for sorting
    # string order   Sort order for results (ascending or descending)
    # return void
    def resultsSorting(self, field, order):

        field = field.strip().lower()
        order = order.strip()
        self.sortField = field
        self.sortOrder = order

    # shortcut method for assigning search parameters and values
    # string field   Field used for searching
    # string value   Text to query
    # return void
    def searchField(self, field, value):

        field = field.strip().lower()
        if field in self.allowedSearchFields:
            self.addParameter(field, value)
        else:
            print("Searches against field " + field + " are not supported")

    # string value   Abstract text to query
    # return void
    def abstractText(self, value):

        self.addParameter('abstract', value)

    # string value   Affiliation text to query
    # return void
    def affiliationText(self, value):

        self.addParameter('affiliation', value)

    # string value   Article number to query
    # return void
    def articleNumber(self, value):

        self.addParameter('article_number', value)

    # string value   Article title to query
    # return void
    def articleTitle(self, value):

        self.addParameter('article_title', value)

    # string value   Author to query
    # return void
    def authorText(self, value):

        self.addParameter('author', value)

    # string value   Author Facet text to query
    # return void
    def authorFacetText(self, value):

        self.addParameter('d-au', value)

    # string value   Value(s) to use in the boolean query
    # return void
    def booleanText(self, value):

        self.addParameter('boolean_text', value)

    # string value   Content Type Facet text to query
    # return void
    def contentTypeFacetText(self, value):

        self.addParameter('d-pubtype', value)

    # string value   DOI (Digital Object Identifier) to query
    # return void
    def doi(self, value):

        self.addParameter('doi', value)

    # string value   Facet text to query
    # return void
    def facetText(self, value):

        self.addParameter('facet', value)

    # string value   Author Keywords, IEEE Terms, and Mesh Terms to query
    # return void
    def indexTerms(self, value):

        self.addParameter('index_terms', value)

    # string value   ISBN (International Standard Book Number) to query
    # return void
    def isbn(self, value):

        self.addParameter('isbn', value)

    # string value   ISSN (International Standard Serial number) to query
    # return void
    def issn(self, value):

        self.addParameter('issn', value)

    # string value   Issue number to query
    # return void
    def issueNumber(self, value):

        self.addParameter('is_number', value)

    # string value   Text to query across metadata fields and the abstract
    # return void
    def metaDataText(self, value):

        self.addParameter('meta_data', value)

    # string value   Publication Facet text to query
    # return void
    def publicationFacetText(self, value):

        self.addParameter('d-year', value)

    # string value   Publisher Facet text to query
    # return void
    def publisherFacetText(self, value):

        self.addParameter('d-publisher', value)

    # string value   Publication title to query
    # return void
    def publicationTitle(self, value):

        self.addParameter('publication_title', value)

    # string or number value   Publication year to query
    # return void
    def publicationYear(self, value):

        self.addParameter('publication_year', value)

    # string value   Text to query across metadata fields, abstract and document text
    # return void
    def queryText(self, value):

        self.addParameter('querytext', value)

    # string value   Thesaurus terms (IEEE Terms) to query
    # return void
    def thesaurusTerms(self, value):

        self.addParameter('thesaurus_terms', value)

    # add query parameter
    # string parameter   Data field to query
    # string value       Text to use in query
    # return void
    def addParameter(self, parameter, value):

        value = value.strip()

        if (len(value) > 0):

            self.parameters[parameter] = value

            # viable query criteria provided
            self.queryProvided = True

            # set flags based on parameter
            if (parameter == 'article_number'):
                self.usingArticleNumber = True

            if (parameter == 'boolean_text'):
                self.usingBoolean = True

            if (
                    parameter == 'facet' or parameter == 'd-au' or parameter == 'd-year' or parameter == 'd-pubtype' or parameter == 'd-publisher'):
                self.usingFacet = True

    # Open Access document
    # string article   Article number to query
    # return void
    def openAccess(self, article):

        self.usingOpenAccess = True
        self.queryProvided = True
        self.articleNumber(article)

    # calls the API
    # string debugMode  If this mode is on (True) then output query and not data
    # return either raw result string, XML or JSON object, or array
    def callAPI(self, debugModeOff=True):

        if self.usingOpenAccess is True:

            str = self.buildOpenAccessQuery()

        else:

            str = self.buildQuery()

        if debugModeOff is False:

            return str

        else:

            if self.queryProvided is False:
                print("No search criteria provided")

            data = self.queryAPI(str)
            formattedData = self.formatData(data)
            return formattedData

    # creates the URL for the Open Access Document API call
    # return string: full URL for querying the API
    def buildOpenAccessQuery(self):

        url = self.openAccessEndPoint;
        url += str(self.parameters['article_number']) + '/fulltext'
        url += '?apikey=' + str(self.apiKey)
        url += '&format=' + str(self.outputType)

        return url

    # creates the URL for the non-Open Access Document API call
    # return string: full URL for querying the API
    def buildQuery(self):

        url = self.endPoint;

        url += '?apikey=' + str(self.apiKey)
        url += '&format=' + str(self.outputType)
        url += '&max_records=' + str(self.resultSetMax)
        url += '&start_record=' + str(self.startRecord)
        url += '&sort_order=' + str(self.sortOrder)
        url += '&sort_field=' + str(self.sortField)

        # add in search criteria
        # article number query takes priority over all others
        if (self.usingArticleNumber):

            url += '&article_number=' + str(self.parameters['article_number'])

        # boolean query
        elif (self.usingBoolean):

            url += '&querytext=(' + urllib.parse.quote_plus(self.parameters['boolean_text']) + ')'

        else:

            for key in self.parameters:

                if (self.usingFacet and self.facetApplied is False):

                    url += '&querytext=' + urllib.parse.quote_plus(self.parameters[key]) + '&facet=' + key
                    self.facetApplied = True

                else:

                    url += '&' + key + '=' + urllib.parse.quote_plus(self.parameters[key])

        # add in filters
        for key in self.filters:
            url += '&' + key + '=' + str(self.filters[key])
        print(url)
        return url

    # creates the URL for the API call
    # string url  Full URL to pass to API
    # return string: Results from API
    def queryAPI(self, url):

        content = urllib2.urlopen(url).read()
        return content

    # formats the data returned by the API
    # string data    Result string from API
    def formatData(self, data):

        if self.outputDataFormat == 'raw':
            return data

        elif self.outputDataFormat == 'object':

            if self.outputType == 'xml':
                obj = ET.ElementTree(ET.fromstring(data))
                return obj

            else:
                obj = json.loads(data)
                return obj

        else:
            return data


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
    request.session['conference_name'] = conf_name
    request.session['conference_year'] = year_name
    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        context = data_frame.to_dict('records')

        return render(request, "Home/second.html", {'records': context,'name':request.session['conference_name']})

    driver = webdriver.Chrome()
    query = "https://dblp.uni-trier.de/search?q=" + str(conf_name)
    #driver.get("https://dblp.uni-trier.de/search?q=asp-dac")
    driver.get(query)
    divs = driver.find_elements(By.CLASS_NAME, 'result-list')

    result = []
    for i in divs[0].find_elements(By.TAG_NAME, 'a'):
        result.append(i.get_attribute('href'))

    driver.get(result[0])
    all_header = []
    year = []
    Sources = []
    title = driver.find_element(By.CLASS_NAME, 'title')
    title = title.text
    place = title.split(",")[-3]
    header = driver.find_elements(By.CLASS_NAME, 'publ-list')
    #print(str(year_name))
    for i in header:
        #print(type(i.find_elements_by_tag_name('span')[4].text))
        #if i.find_elements(By.TAG_NAME, 'span')[4].text == str(year_name):
        if str(year_name) in i.find_elements(By.TAG_NAME, 'span')[4].text:
            year.append(i.find_elements(By.TAG_NAME, 'span')[4].text)
            Sources.append(i.find_elements(By.TAG_NAME, 'span')[3].text)
            element = i.find_element(By.CLASS_NAME, 'toc-link')
            all_header.append(element.get_attribute('href'))
            #print('hi')
        #print(element.get_attribute('href'))
    author_name = []
    paper_name = []
    years = []
    sources = []
    paperlinks = []
    google_scholar_link_paper = []

    for i in range(len(all_header)):
        driver.get(all_header[i])
        header = driver.find_elements(By.CLASS_NAME, 'inproceedings')
        for j in range(len(header)):
            hyperlinks = header[j].find_element(By.TAG_NAME, 'nav').find_elements(By.TAG_NAME, 'a')
            paperlinks.append(hyperlinks[1].get_attribute('href'))
            ele = header[j].find_element(By.TAG_NAME, 'nav').find_elements(By.CLASS_NAME, 'drop-down')
            newEle = ele[2].find_elements(By.TAG_NAME, 'div')[1].find_elements(By.TAG_NAME, 'a')
            google_scholar_link_paper.append(newEle[1].get_attribute('href'))

            paper_name.append(header[j].find_element(By.CLASS_NAME, 'title').text)
            years.append(year[i])
            sources.append(Sources[i])
            temp = []
            for k in header[j].find_elements(By.TAG_NAME, 'a'):
                if k.text:
                    temp.append(k.text)
                    authors.append(k.text)
            temp = ', '.join(temp)
            author_name.append(temp)
    citation_google_scholar = []
    queryR = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C33&q='

    for i in range(len(paper_name)):
        params = {
            "engine": "google_scholar",
            "q": paper_name[i],
            #"api_key": "995e3752065c294040ed68a430e17bb456f20d77e991ab3db02d19bd55899beb",
            "api_key": "db7f447d55c6727123e336a4d52477f4b8098fa4abb35c749c1cb719dcb839e0",
            "start": 0
            #  "num":20
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        try:
            if results['organic_results'] and 'cited_by' in results['organic_results'][0]['inline_links'].keys():
                organic_results = results['organic_results']
                keys = organic_results[0]['inline_links'].keys()
                citation_google_scholar.append(organic_results[0]['inline_links']['cited_by']['total'])
            else:
                citation_google_scholar.append(0)
        except:
            citation_google_scholar.append(0)
    citation_openalex = []
    citation_ieee_xplore = []
    ieeeQuery = XPLORE('3jzsb6mqekx5skc7pgr8nyqf')

    for i in range(len(paper_name)):
        string_url = paper_name[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?filter=title.search:' + string_url

        data = requests.get(url)
        data = data.json()
        try:
            d = data['results'][0]
            citation_openalex.append(d['cited_by_count'])
        except:
            citation_openalex.append(0)


        ieeeQuery.articleTitle(paper_name[i])
        data = ieeeQuery.callAPI()
        dict_str = data.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)
        try:
            if mydata['articles'][0]['citing_paper_count']:
                citation_ieee_xplore.append(mydata['articles'][0]['citing_paper_count'])
            else:
                citation_ieee_xplore.append(0)
        except:
            citation_ieee_xplore.append(0)

    data_frame = pd.DataFrame({
        #'Authors': author_name,
        'PaperName': paper_name,
        'Year': years,  # [year[0]]*len(author_name),
        'sources': sources,
        'place': [place]*len(sources),
        'authors': author_name,
        'hyperlink': paperlinks,
        'citationG':citation_google_scholar,
        'citationO':citation_openalex,
        'citationI':citation_ieee_xplore
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

    return render(request, "Home/second.html", {'records':context, 'name':request.session['conference_name']})


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
    #detector = gender.Detector()
    #gender_data = []
    #data = pd.read_csv(str(request.session['file_name_author']))
    #authors = list(data['Authors'])
    #url = 'https://api.genderize.io?name='
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
    return render(request, "Home/piechart.html",{'name':request.session['conference_name']})

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
                   'topcitation': top_five_citations,'name':request.session['conference_name']
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
                   'lastcitation': last_five_citations,'name':request.session['conference_name']})


def statisticsMostCommonAuthor(request):
    data = pd.read_csv(str(request.session['file_name']))

    file_name = str(request.session['file_name'])[:-4] + 'statisticsMostCommonAuthor'
    saved_file_name = file_name + '.csv'
    request.session['file_name_MCAstatistics'] = saved_file_name

    if os.path.exists(saved_file_name):
        data_frame = pd.read_csv(saved_file_name)
        top_rows = data_frame.to_dict('records')

        return render(request, "Home/statisticsMostCommonAuthor.html",
                      {'toprows': top_rows,'name':request.session['conference_name']
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
                  {'toprows': top_rows,'name':request.session['conference_name']
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
                          'lastrows': last_rows,'name':request.session['conference_name']
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
                   'lastrows': last_rows,'name':request.session['conference_name']
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
                          'toppaper': top_five_citations,'name':request.session['conference_name']
                      })

    papers = list(dataset['PaperName'])
    citations_per_paper = []

    for i in range(len(papers)):
        string_url = papers[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?filter=title.search:' + string_url

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
                      'toppaper': top_five_citations,'name':request.session['conference_name']
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
                          'lastpaper': last_five_citations,'name':request.session['conference_name']
                      })

    papers = list(dataset['PaperName'])
    citations_per_paper = []

    for i in range(len(papers)):
        string_url = papers[i]
        string_url = string_url.replace(" ", "+")
        url = 'https://api.openalex.org/works?filter=title.search:' + string_url

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
                      'lastpaper':last_five_citations,'name':request.session['conference_name']
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
        url = 'https://api.openalex.org/works?filter=title.search:' + string_url
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

    return render(request, "Home/authorStatistics.html",{'context':data,'name':request.session['conference_name']})

def bestPaper(request):
    driver = webdriver.Chrome()
    driver.get('https://jeffhuang.com/best_paper_awards/')
    year_name = request.session['conference_year']
    #cf_name = request.session['conference_name']
    subresult = driver.find_elements(By.ID,year_name)
    subres = subresult[0].find_elements(By.TAG_NAME, 'tr')

    conference_name = []
    for i in range(1, len(subres)):
        temp = []
        for j in subres[i].find_elements(By.TAG_NAME, 'th'):
            temp.append(j.text)
        for j in subres[i].find_elements(By.TAG_NAME, 'td'):
            temp.append(j.text.split("; ")[0])
        conference_name.append(temp)
    cf_name = []
    paper_name = []
    author_name = []
    for i in range(len(conference_name)):
        if len(conference_name[i]) > 2:
            cf_name.append(conference_name[i][0])
            paper_name.append(conference_name[i][1])
            author_name.append(conference_name[i][2])
        else:
            cf_name.append(conference_name[i-1][0])
            paper_name.append(conference_name[i][0])
            author_name.append(conference_name[i][1])
    df_conference = pd.DataFrame({
        'cfName':cf_name,
        'paperName':paper_name,
        'authorName':author_name
    })
    data = df_conference.to_dict('records')
    return render(request, "Home/bestPaper.html", {'context':data,'conf_year':year_name})