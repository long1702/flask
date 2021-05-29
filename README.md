# Spam_Moniter_System

## Database Schema:

### Topic:
```
{
    _id: {
            type: String,
            default: uuidv4,
        },
    topic_id : String,
    crawl_period: { type: Number, default: 86400},
    next_crawl_at: Date
}
```
### Mention
```
{ 
    _id: {
            type: String,
            default: uuidv4,
        },
    topic_id: String,
    mention_id: String,
    mention_type: Number,
    true_label: Boolean,
    created_date: Date, 
    is_updated: Boolean,
    predict: [{
        label: Boolean,
        confident_score: Number,
        model: String,
        sent_date: Date
    }]  
}
```

## Request:
```
Route: /spam-data
{   
    items: [{
        topic: String,
        mention_type: Number,
        mention_id: String,
        label: String,
        confident_score: Number,
        model: String
    }]
}
