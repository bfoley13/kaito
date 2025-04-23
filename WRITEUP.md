# Integrating Azure AI Search into KAITO

## BYO AI Search Indexes

Bring Your Own (BYO) AI Search Indexes allow you to integrate your existing Azure AI Search indexes into KAITO. This approach is ideal if you already have a well-defined search infrastructure and want to leverage KAITO's capabilities without migrating your data.

### Steps to Integrate:
1. **Create or Use an Existing Azure AI Search Index**  
   Ensure your vector indexs are properly configured in Azure. Follow docementation at [Vectors in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-overview) for optimal performance.

2. **Provide Azure AI Search Details to KAITO**  
   Supply the following details to KAITO RAGEngine Definition:
   - Azure AI Search uri
   - Azure AI Search key
   - Index Definitions:
      - Name
      - id field
      - chunk field
      - embedding field
      - metadata field
      - document id field

3. **Test the Integration**  
   Verify that KAITO can query your Azure AI Search Vector indexes:
    ```
    kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- curl -X POST http://$CLUSTERIP/query -H "accept: application/json" -H "Content-Type: application/json" -d '{"index_name":"<your_index>","query":"<sample_query>"}'
    ```

### Limitations

- Creating New Indexes through KAITO will not leverage any existing Embedding Models or skills used within other Indexes
- You cannot add documents to indexes you created outside of kaito

## KAITO Managed Indexes

KAITO Managed Indexes simplify the process by allowing KAITO to handle the creation and management of Azure AI Search indexes on your behalf. This is a great option if you prefer a hands-off approach to managing indexes.

### Steps to Use KAITO Managed Indexes:
1. **Provide Azure AI Search Details to KAITO**  
   Supply the following details to KAITO RAGEngine Definition:
   - Azure AI Search uri
   - Azure AI Search key

2. **Create an Index and Add Documents**  
   Use the following command to create an index with a document:

   ```
    kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- curl -X POST http://$CLUSTERIP/index -H "accept: application/json" -H "Content-Type: application/json" -d '{
        "index_name": "kaito",
        "documents": [
            {
                "text": "Kaito is an operator that automates the AI/ML model inference or tuning workload in a Kubernetes cluster",
                "metadata": {"author": "kaito", "category": "kaito"}
            }
        ]
    }
   ```

3. **Test the Integration**  
   Verify that KAITO can the index you just created:
    ```
    kubectl run -it --rm --restart=Never curl --image=curlimages/curl -- curl -X POST http://$CLUSTERIP/query -H "accept: application/json" -H "Content-Type: application/json" -d '{"index_name":"kaito","query":"what is kaito?"}'
    ```

### Benefits of KAITO Managed Indexes:
- Handles Index creation with default field parameters.
- Handles document embedding/creation within the index
- Reduced operational overhead and cost of hosting embedding models in Azure OpenAI
