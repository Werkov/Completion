#include <iostream>
#include <string>

using namespace std;

class ILetterModel {
public:
	virtual void setText(const string & text) = 0;
	virtual void setPosition(int i) = 0;
	virtual int getOrder(char c) = 0;
};

class UniformModel : public ILetterModel{
public:
	void setText(const string & text)
	{
		this->s = text;
	}

	void setPosition(int i) {}

	int getOrder(char c) 
	{
		if(c == ' ')
			return 27;
		else
			return c - 'a' + 1;
	}

private:
	string s;
};

class FreqModel : public ILetterModel{
public:
	FreqModel() : freq( "eoainstrvulzdkpmcyhjbgfxwqK") {}

	void setText(const string & text)
	{
		this->s = text;
	}

	void setPosition(int i) {}

	int getOrder(char c) 
	{
		int o = 0;
		while(this->s[o] != c && this->s[o] != 'K')
		{
			++o;
		}
		
		return o + 1;
	}

private:
	string s;
	string freq;
};

int main(int argc, char ** argv)
{
	string input = "nejaky text s abecedou";
	UniformModel m;
	//FreqModel m;
	m.setText(input);
		
	int dist = 0;
	for(unsigned int i = 0; i < input.length() - 1; ++i)
	{
		m.setPosition(i);
		dist += m.getOrder(input[i + 1]);
	}

	cout << dist << endl;
	return 0;
}
