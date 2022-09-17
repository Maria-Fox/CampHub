# # # # # # # # # # # # # # # # # # # # # # # # # # Serialize comments
# serialize into json readable items - converts to instances of a dictionary

def serialize(self):
    '''Serialzie comments'''

    return {
      "comment_user_id": self.comment_user_id,
      "content": self.content
    }

def user_post_serialize(self):
  '''Serialize the user posts'''
  
  return {
    "author_id" : self.author_id,
    "title": self.title,
    "content": self.content
  }