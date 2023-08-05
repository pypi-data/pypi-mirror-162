def learn_all():
    print(" 1.Linear regression analysis"
     "1.1< is used to predict the value of a variable based on the value of another variable" 
    "1.2< The variable you want to predict is called the dependent variable."
    "1.3< The variable you are using to predict the other variable's value is called the independent variable."
    "1.4< y=mx+c   where y is the dependent variable and x is the independent variable and c is the intercept , m is the slope" 



    "To Import : sklearn.linear_model.LinearRegression(*, fit_intercept=True, normalize='deprecated', copy_X=True, n_jobs=None, positive=False)"

             "The coefficient of determination R2  is defined as  ( 1-u/v)"

                "where  is the residual sum of squares((y_true - y_pred)** 2).sum() and  is the total sum of squares ((y_true - y_true.mean()) ** 2).sum()"

            "The best possible score is 1.0"
                "A constant model that always predicts the expected value of y, disregarding the input features, would get a  score of 0.0."


    "***************************************************************************************************************"
    
    "2. Logistic Regression Analysis"
    "2.1< Linear Regression is all about fitting a straight line in the data while Logistic Regression is about fitting a curve to the data."
    "2.2< Linear Regression is a regression algorithm for Machine Learning while Logistic Regression is a classification Algorithm for machine learning."
    "2.3< Logistic Regression is used when the dependent variable(target) is categorical." 
    "2.4< For example, To predict whether an email is spam (1) or (0) Whether the tumor is malignant (1) or not (0)"
    "2.5< graph of Sigmoid function gives much clear idea of the logistic regression"
    "2.6< totally works of the Binary outcomes i.e O or 1 , yes or no, True or false and so on"
    "2.7< Note that regularization is applied by default"

    "To import "
     "class sklearn.linear_model.LogisticRegression(penalty='l2', *, dual=False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1, class_weight=None, random_state=None, solver='lbfgs', max_iter=100, multi_class='auto', verbose=0, warm_start=False, n_jobs=None, l1_ratio=None)"

    "*********************************************************************************************************************"

    "3. Decision Tree "
     "3.1< Decision Tree is the most powerful and popular tool for classification and prediction." 
     "3.2< A Decision tree is a flowchart-like tree structure, where each internal node denotes a test on an attribute, each branch represents an outcome of the test, and each leaf node (terminal node) holds a class label. "
     "3.3< Supervised Machine Learning Algorithm "
      "A general algorithm for a decision tree can be described as follows:"

        "Pick the best attribute/feature. The best attribute is one which best splits or separates the data."
        "Ask the relevant question."
        "Follow the answer path."
        "Go to step 1 until you arrive to the answer."

        "The best split is one which separates two different labels into two sets."

        "------------------------------"
       "|" "GINI INDEX : Gini impurity is an important measure used to construct the decision trees. "
       "|"  "Gini impurity is a function that determines how well a decision tree was split. "
       "|"     "Basically, it helps us to determine which splitter is best so that we can build a pure decision tree. "
       "|"       "Gini impurity ranges values from 0 to 0.5."
       "|"            
       "|"            
       "|"                
        
        "Example"
                                        " from sklearn import tree"
                                        "X = [[0, 0], [1, 1]]"
                                        "Y = [0, 1]"
                                        "clf = tree.DecisionTreeClassifier()"
                                        "clf = clf.fit(X, Y)"
            




            "We can also export the tree in Graphviz format using the export_graphviz exporter." 
            "If you use the conda package manager, the graphviz binaries and the python package can be installed with conda install python-graphviz.")


    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    